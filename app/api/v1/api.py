# dwc_pos/app/api/v1/api.py

from fastapi import APIRouter

from .endpoints import auth # Import your auth router

api_router = APIRouter()

# Include authentication router
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# You will include other routers here later (products, categories, etc.)
# from app.api.v1.endpoints import users, products, categories
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(products.router, prefix="/products", tags=["Products"])
# api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])