# app/db/base.py

from app.db.connection import Base
# Import *semua* model SQLAlchemy Anda di sini
# agar SQLAlchemy dapat menemukannya saat metadata dikumpulkan dan relasi diinisialisasi.

from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission

# Tambahkan import untuk model lain di masa depan saat Anda membuatnya
# from app.models.category import Category
# from app.models.product import Product
# from app.models.customer import Customer
# from app.models.order import Order
# from app.models.order_item import OrderItem
# from app.models.payment import Payment