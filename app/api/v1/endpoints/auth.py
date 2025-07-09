# app/api/v1/endpoints/auth.py

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.connection import get_db
from app.models.user import User as UserModel
from app.models.company import Company as CompanyModel
from app.schemas.user import UserCreate, User as UserSchema
from app.schemas.token import Token
from app.core.config import settings # <--- INI PENTING: Import settings di sini
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token
    # Hapus ACCESS_TOKEN_EXPIRE_MINUTES dari sini karena diakses via settings
)

router = APIRouter()

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    Hashes the password and checks for duplicate username or email.
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

    # Hash the password
    hashed_password = get_password_hash(user_in.password)
    
    # Create the user model instance
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

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint to get an OAuth2 access token.
    """
    user = await db.execute(
        select(UserModel)
        .options(selectinload(UserModel.company)) # Eager load company saat login
        .where(UserModel.username == form_data.username, UserModel.is_active == True)
    )
    user = user.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create an access token using settings.ACCESS_TOKEN_EXPIRE_MINUTES
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "is_superuser": user.is_superuser, "company_id": user.company_id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}