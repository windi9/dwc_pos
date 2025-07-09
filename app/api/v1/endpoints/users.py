# app/api/v1/endpoints/users.py

from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext # Untuk hashing password

from app.db.connection import get_db
from app.models.user import User as UserModel
from app.models.company import Company as CompanyModel # Untuk validasi company_id
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema

router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    # current_user: Any = Depends(get_current_active_user) # Akan diaktifkan nanti
):
    """
    Create a new User.
    Automatically hashes the password.
    Requires company_id to be valid if provided.
    """
    # Validate company_id if provided
    if user_in.company_id is not None:
        company = await db.execute(
            select(CompanyModel).where(CompanyModel.id == user_in.company_id, CompanyModel.is_active == True)
        )
        if not company.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {user_in.company_id} not found or is inactive."
            )

    # Check for duplicate username or email
    existing_user = await db.execute(
        select(UserModel).where(
            (UserModel.username == user_in.username) | (UserModel.email == user_in.email)
        )
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username or email already exists."
        )

    hashed_password = get_password_hash(user_in.password)
    db_user = UserModel(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        company_id=user_in.company_id,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    # Eager load the company relationship for the response
    loaded_user_result = await db.execute(
        select(UserModel)
        .options(selectinload(UserModel.company))
        .where(UserModel.id == db_user.id)
    )
    loaded_user = loaded_user_result.scalar_one()

    return loaded_user

@router.get("/", response_model=List[UserSchema])
async def read_users(
    db: AsyncSession = Depends(get_db),
    company_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    # current_user: Any = Depends(get_current_active_user) # Akan diaktifkan nanti
):
    """
    Retrieve a list of Users, with optional filters.
    """
    query = select(UserModel).options(selectinload(UserModel.company)) # Eager load company
    
    if company_id is not None:
        query = query.where(UserModel.company_id == company_id)
    if is_active is not None:
        query = query.where(UserModel.is_active == is_active)
    if is_superuser is not None:
        query = query.where(UserModel.is_superuser == is_superuser)

    result = await db.execute(query.offset(skip).limit(limit))
    users = result.scalars().unique().all()
    return users

@router.get("/{user_id}", response_model=UserSchema)
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: Any = Depends(get_current_active_user) # Akan diaktifkan nanti
):
    """
    Retrieve a single User by ID.
    """
    result = await db.execute(
        select(UserModel)
        .options(selectinload(UserModel.company)) # Eager load company
        .where(UserModel.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    # current_user: Any = Depends(get_current_active_user) # Akan diaktifkan nanti
):
    """
    Update an existing User.
    Password will be re-hashed if provided.
    """
    result = await db.execute(
        select(UserModel)
        .options(selectinload(UserModel.company)) # Eager load company
        .where(UserModel.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Validate company_id if provided and changed
    if user_in.company_id is not None and user_in.company_id != user.company_id:
        company = await db.execute(
            select(CompanyModel).where(CompanyModel.id == user_in.company_id, CompanyModel.is_active == True)
        )
        if not company.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {user_in.company_id} not found or is inactive."
            )

    # Check for duplicate username or email, excluding current user
    if user_in.username is not None and user_in.username != user.username:
        existing_username = await db.execute(
            select(UserModel).where(
                UserModel.username == user_in.username,
                UserModel.id != user_id
            )
        )
        if existing_username.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username already exists."
            )
    
    if user_in.email is not None and user_in.email != user.email:
        existing_email = await db.execute(
            select(UserModel).where(
                UserModel.email == user_in.email,
                UserModel.id != user_id
            )
        )
        if existing_email.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists."
            )

    # Update password if provided
    if user_in.password:
        user.hashed_password = get_password_hash(user_in.password)
        # Jangan set user_in.password ke user, karena itu adalah raw password
        del user_in.password # Hapus dari objek user_in agar tidak disalin langsung

    # Update other attributes
    for field, value in user_in.model_dump(exclude_unset=True).items():
        if field != "password": # Pastikan password tidak disalin jika ada di user_in
            setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: Any = Depends(get_current_active_user) # Akan diaktifkan nanti
):
    """
    Deactivate (soft delete) a User.
    """
    result = await db.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    user.deleted_at = func.now()
    await db.commit()
    return {"message": "User deactivated successfully"}