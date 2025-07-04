# app/api/v1/endpoints/uoms.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.connection import get_db
from app.models.uom import UOM as UOMModel # Alias untuk menghindari konflik nama
from app.schemas.uom import UOMCreate, UOMUpdate, UOM as UOMSchema # Alias untuk skema output
# from app.core.security import get_current_active_user # Akan kita tambahkan nanti untuk otentikasi

router = APIRouter()

@router.post("/", response_model=UOMSchema, status_code=status.HTTP_201_CREATED)
async def create_uom(
    uom_in: UOMCreate,
    db: AsyncSession = Depends(get_db),
    # current_user: Any = Depends(get_current_active_user) # Aktifkan ini nanti
):
    """
    Create a new Unit of Measure (UOM).
    """
    # Cek apakah nama atau simbol UOM sudah ada
    existing_uom = await db.execute(
        select(UOMModel).where(
            (UOMModel.name == uom_in.name) | (UOMModel.symbol == uom_in.symbol)
        )
    )
    if existing_uom.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="UOM with this name or symbol already exists."
        )

    db_uom = UOMModel(**uom_in.model_dump())
    db.add(db_uom)
    await db.commit()
    await db.refresh(db_uom)
    return db_uom

@router.get("/", response_model=List[UOMSchema])
async def read_uoms(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # current_user: Any = Depends(get_current_active_user) # Aktifkan ini nanti
):
    """
    Retrieve a list of all Units of Measure (UOMs).
    """
    result = await db.execute(
        select(UOMModel).offset(skip).limit(limit)
    )
    uoms = result.scalars().all()
    return uoms

@router.get("/{uom_id}", response_model=UOMSchema)
async def read_uom_by_id(
    uom_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: Any = Depends(get_current_active_user) # Aktifkan ini nanti
):
    """
    Retrieve a single Unit of Measure (UOM) by its ID.
    """
    result = await db.execute(
        select(UOMModel).where(UOMModel.id == uom_id)
    )
    uom = result.scalar_one_or_none()
    if not uom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UOM not found"
        )
    return uom