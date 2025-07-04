# app/api/v1/endpoints/products.py

from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload # Penting untuk eager loading relasi

from app.db.connection import get_db
from app.models.product import Product as ProductModel
from app.models.company import Company as CompanyModel # Perlu diimpor untuk validasi
from app.models.uom import UOM as UOMModel # Perlu diimpor untuk validasi
from app.schemas.product import ProductCreate, ProductUpdate, Product as ProductSchema

router = APIRouter()

@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    # current_user: Any = Depends(get_current_active_user) # Aktifkan ini nanti
):
    """
    Create a new Product.
    Requires company_id and stock_uom_id to be valid.
    """
    # Validate company_id
    company = await db.execute(
        select(CompanyModel).where(CompanyModel.id == product_in.company_id, CompanyModel.is_active == True)
    )
    if not company.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {product_in.company_id} not found or is inactive."
        )

    # Validate stock_uom_id
    uom = await db.execute(
        select(UOMModel).where(UOMModel.id == product_in.stock_uom_id, UOMModel.is_active == True)
    )
    if not uom.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"UOM with ID {product_in.stock_uom_id} not found or is inactive."
        )

    # Check for duplicate product name or SKU within the same company
    existing_product = await db.execute(
        select(ProductModel).where(
            ProductModel.company_id == product_in.company_id,
            (ProductModel.name == product_in.name) | (ProductModel.sku == product_in.sku)
        )
    )
    if existing_product.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product with this name or SKU already exists for this company."
        )

    db_product = ProductModel(**product_in.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    # <--- MULAI PERUBAHAN DI SINI --->
    # Query ulang untuk memuat relasi stock_uom dengan eager loading
    # Ini akan memastikan objek db_product yang dikembalikan memiliki relasi stock_uom yang sudah dimuat
    loaded_product_result = await db.execute(
        select(ProductModel)
        .options(selectinload(ProductModel.stock_uom))
        .where(ProductModel.id == db_product.id)
    )
    loaded_product = loaded_product_result.scalar_one() # Gunakan scalar_one karena kita tahu pasti ada
    # <--- AKHIR PERUBAHAN --->

    return loaded_product

@router.get("/", response_model=List[ProductSchema])
async def read_products(
    db: AsyncSession = Depends(get_db),
    company_id: Optional[int] = None, # Filter by company_id
    is_active: Optional[bool] = None, # Filter by active status
    skip: int = 0,
    limit: int = 100,
    # current_user: Any = Depends(get_current_active_user) # Aktifkan ini nanti
):
    """
    Retrieve a list of Products, with optional filtering by company_id and active status.
    """
    query = select(ProductModel).options(selectinload(ProductModel.stock_uom)) # Eager load UOM
    
    if company_id is not None:
        query = query.where(ProductModel.company_id == company_id)
    if is_active is not None:
        query = query.where(ProductModel.is_active == is_active)

    result = await db.execute(query.offset(skip).limit(limit))
    products = result.scalars().unique().all() # .unique() needed when using selectinload
    return products

@router.get("/{product_id}", response_model=ProductSchema)
async def read_product_by_id(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: Any = Depends(get_current_active_user) # Aktifkan ini nanti
):
    """
    Retrieve a single Product by its ID.
    """
    result = await db.execute(
        select(ProductModel)
        .options(selectinload(ProductModel.stock_uom)) # Eager load UOM
        .where(ProductModel.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    # current_user: Any = Depends(get_current_active_user) # Aktifkan ini nanti
):
    """
    Update an existing Product.
    """
    result = await db.execute(
        select(ProductModel)
        .options(selectinload(ProductModel.stock_uom)) # Eager load UOM
        .where(ProductModel.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Validate company_id if provided and changed
    if product_in.company_id is not None and product_in.company_id != product.company_id:
        company = await db.execute(
            select(CompanyModel).where(CompanyModel.id == product_in.company_id, CompanyModel.is_active == True)
        )
        if not company.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with ID {product_in.company_id} not found or is inactive."
            )

    # Validate stock_uom_id if provided and changed
    if product_in.stock_uom_id is not None and product_in.stock_uom_id != product.stock_uom_id:
        uom = await db.execute(
            select(UOMModel).where(UOMModel.id == product_in.stock_uom_id, UOMModel.is_active == True)
        )
        if not uom.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"UOM with ID {product_in.stock_uom_id} not found or is inactive."
            )

    # Check for duplicate name or SKU within the same company, excluding current product
    if product_in.name is not None and product_in.name != product.name:
        existing_name = await db.execute(
            select(ProductModel).where(
                ProductModel.company_id == product.company_id,
                ProductModel.name == product_in.name,
                ProductModel.id != product_id
            )
        )
        if existing_name.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product with this name already exists for this company."
            )

    if product_in.sku is not None and product_in.sku != product.sku:
        existing_sku = await db.execute(
            select(ProductModel).where(
                ProductModel.company_id == product.company_id,
                ProductModel.sku == product_in.sku,
                ProductModel.id != product_id
            )
        )
        if existing_sku.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product with this SKU already exists for this company."
            )

    # Update attributes that are provided in the request
    for field, value in product_in.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: Any = Depends(get_current_active_user) # Aktifkan ini nanti
):
    """
    Deactivate (soft delete) a Product.
    """
    result = await db.execute(
        select(ProductModel).where(ProductModel.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product.is_active = False
    product.deleted_at = func.now()
    await db.commit()
    return {"message": "Product deactivated successfully"}