# app/api/v1/endpoints/auth.py

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession # IMPOR BARU UNTUK ASYNC
from sqlalchemy import select # IMPOR BARU UNTUK ASYNC QUERYING

from app.db.connection import get_db
from app.core.config import settings
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, decode_access_token,
    generate_verification_token, generate_verification_code,
    get_pin_hash, verify_pin
)
from app.schemas.auth import Token, UserLogin, UserRegister, VerifyEmailLink, VerifyLoginCode, UserPinLogin
from app.schemas.user import UserResponse
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.user_role import UserRole

# Import placeholder for email sending service (ensure this file exists and contains the async functions)
from app.services.email_service import send_email_verification_link, send_email_verification_code

router = APIRouter()

# Dependency to get the current user based on JWT token
# (This will be expanded to check roles/permissions later)
async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token"))):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # UBAH QUERY SINKRON MENJADI ASYNC
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalar_one_or_none() # Mengambil satu hasil atau None

    if user is None:
        raise credentials_exception
    
    # Basic check for active user
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    return user

# Dependency to get current active user (e.g., for general protected endpoints)
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

# Dependency to check for specific roles (will be more complex with RBAC permissions)
# For now, a simplified version based on 'is_admin' or role name
async def get_current_superadmin_user(current_user: User = Depends(get_current_active_user)):
    # Untuk mendapatkan peran user, kita perlu memuat relasi 'roles'
    # SQLAlchemy 2.0+ mendukung lazy loading, tapi untuk pemeriksaan segera,
    # kita bisa memuatnya secara eksplisit atau memastikan relasi terload.
    
    # Jika relasi belum terload, ini akan memuatnya:
    # await current_user.awaitable_attrs.roles # Pastikan relasi sudah terload

    # Cek apakah user memiliki peran 'Superadmin'
    for user_role_association in current_user.roles:
        # PENTING: Untuk mengakses atribut 'role' dari UserRole,
        # pastikan relasi UserRole.role sudah terload.
        # Jika belum, mungkin perlu eager loading di query awal User,
        # atau load secara eksplisit di sini.
        # Untuk kasus sederhana, jika .roles sudah diakses, kemungkinan besar relasi Role juga terload.
        if user_role_association.role.name == "Superadmin" and user_role_association.role.is_active:
            return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges (requires Superadmin role).")

# --- Authentication Endpoints ---

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    # UBAH QUERY SINKRON MENJADI ASYNC
    existing_user_result = await db.execute(
        select(User).filter(
            (User.username == user_in.username) | (User.email == user_in.email)
        )
    )
    existing_user = existing_user_result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered"
        )
    
    hashed_password = get_password_hash(user_in.password)
    
    # Generate verification token for email activation link
    verification_token = generate_verification_token()
    
    # Create new user with email_verified = False initially
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        phone_number=user_in.phone_number,
        full_name=user_in.full_name,
        is_active=True,
        email_verified=False
        # PIN is not set at registration, it can be set post-login or by admin
    )
    
    db.add(db_user)
    await db.commit() # Gunakan await untuk db.commit() di AsyncSession
    await db.refresh(db_user) # Gunakan await untuk db.refresh()

    # Assign a default role, e.g., 'Employee' atau 'Customer'
    # Untuk kasus awal, mari kita assign sebagai 'Employee' jika role belum ada
    # UBAH QUERY SINKRON MENJADI ASYNC
    default_role_result = await db.execute(select(Role).filter(Role.name == "Employee"))
    default_role = default_role_result.scalar_one_or_none()

    if not default_role:
        # Create default role if it doesn't exist (only for first time setup/seeding)
        # Jika Anda yakin sudah ada seeding untuk roles, blok ini bisa dihilangkan
        print("WARNING: 'Employee' role not found, creating it for new user. Consider seeding roles at startup.")
        default_role = Role(name="Employee", description="Default role for general users/cashiers")
        db.add(default_role)
        await db.commit()
        await db.refresh(default_role)

    user_role_association = UserRole(user_id=db_user.id, role_id=default_role.id)
    db.add(user_role_association)
    await db.commit() # Commit setelah menambah user_role_association
    await db.refresh(db_user) # Refresh db_user untuk memuat relasi roles

    # Send verification email with the link (async task in real app)
    verification_link = f"http://localhost:8000{settings.API_V1_STR}/auth/verify-email?token={verification_token}"
    
    # Simulate sending email
    await send_email_verification_link(db_user.email, verification_link)
    print(f"DEBUG: Email verification link for {db_user.email}: {verification_link}")

    return db_user

@router.get("/verify-email", summary="Verify user email via activation link")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    # In a real app, you'd lookup the token in the database,
    # find the associated user, and mark their email as verified.
    # For this demo, we'll simplify and just try to verify an unverified user.
    
    # UBAH QUERY SINKRON MENJADI ASYNC
    user_to_verify_result = await db.execute(
        select(User).filter(User.email_verified == False)
    )
    user_to_verify = user_to_verify_result.scalar_one_or_none()

    if not user_to_verify:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token, or user already verified."
        )
    
    user_to_verify.email_verified = True
    db.add(user_to_verify) # db.add() tidak perlu await
    await db.commit() # Gunakan await
    await db.refresh(user_to_verify) # Gunakan await

    return {"message": f"Email '{user_to_verify.email}' successfully verified. You can now log in."}


@router.post("/token", response_model=Token, summary="Login for Web Admin (requires email verification)")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db) # UBAH TIPE INI
):
    # Determine if input is username or email
    # UBAH QUERY SINKRON MENJADI ASYNC
    user_result = await db.execute(
        select(User).filter(
            (User.username == form_data.username) | (User.email == form_data.username)
        )
    )
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or email",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )
    
    # --- Web Admin Specific: Email Verification Check & Code Sending ---
    if not user.email_verified:
        # Generate and store verification code temporarily (e.g., in Redis/DB with expiry)
        verification_code = generate_verification_code()
        # In a real app, save this code to DB/cache for later verification
        
        await send_email_verification_code(user.email, verification_code) # Gunakan await
        print(f"DEBUG: Login verification code for {user.email}: {verification_code}")

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. A verification code has been sent to your email. Please use '/api/v1/auth/verify-login-code' to complete login.",
            headers={"X-Verification-Required": "email_code"} # Custom header for frontend
        )
    
    # If email is verified, proceed with token generation
    access_token_expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_MINUTES / (24 * 60)) # Konversi menit ke hari untuk durasi lebih panjang
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/verify-login-code", response_model=Token, summary="Verify 6-digit code for Web Admin login")
async def verify_login_code(
    code_in: VerifyLoginCode,
    db: AsyncSession = Depends(get_db) # UBAH TIPE INI
):
    # UBAH QUERY SINKRON MENJADI ASYNC
    user_result = await db.execute(select(User).filter(User.email == code_in.email))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    # --- Simulate code verification ---
    # In a real app, you'd retrieve the code stored in DB/cache for this user,
    # compare it with code_in.code, and check expiry.
    # For demo, we'll assume any code starting with '123' is valid for 'superadmin@example.com'
    # and for other users any code is valid if email is correct, but only if they just
    # requested a token that resulted in verification_required error.
    if user.email == "superadmin@example.com" and code_in.code == "123456":
         pass # Specific dummy logic for superadmin.
    elif user.email_verified and code_in.code == "123456": # General dummy code for verified users
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired verification code."
        )
    # --- End Simulate code verification ---

    # If code is valid, generate the access token
    access_token_expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_MINUTES / (24 * 60)) # Web Admin persistence
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/pos-login", response_model=Token, summary="Login for POS App (using username/email and PIN)")
async def login_for_pos_app(pin_login_data: UserPinLogin, db: AsyncSession = Depends(get_db)): # UBAH TIPE INI
    # Determine if input is username or email
    # UBAH QUERY SINKRON MENJADI ASYNC
    user_result = await db.execute(
        select(User).filter(
            (User.username == pin_login_data.username_or_email) | (User.email == pin_login_data.username_or_email)
        )
    )
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or email",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify PIN (assuming PIN is stored plaintext for this demo, or hashed in a real app)
    # For production, you might want to hash PINs as well.
    # Jika PIN di-hash:
    if user.pin is None or not verify_pin(pin_login_data.pin, user.pin):
    # Jika PIN plaintext:
    # if user.pin is None or user.pin != pin_login_data.pin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect PIN",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )
    
    # POS App tokens can have a shorter expiry (e.g., 30-60 minutes)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}