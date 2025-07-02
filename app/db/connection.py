# app/db/connection.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.db.base import Base # Import Base dari lokasi yang benar (app.db.base)

# --- PENTING: IMPOR SEMUA MODEL ANDA DI SINI ---
# Ini penting agar SQLAlchemy dan Alembic mendeteksi semua model Anda
# saat engine atau metadata diakses.
import app.models.user
import app.models.role
import app.models.permission
import app.models.user_role
import app.models.role_permission
import app.models.company
import app.models.outlet
# Jika ada model lain yang akan kita buat nanti, tambahkan juga di sini:
# import app.models.product
# import app.models.product_uom_conversion
# import app.models.product_variant
# import app.models.product_outlet
# import app.models.recipe_material
# import app.models.production_order
# import app.models.customer
# import app.models.sales_channel
# import app.models.product_variant_channel_price
# import app.models.add_on
# import app.models.product_variant_add_on
# import app.models.add_on_channel_price
# import app.models.transaction
# import app.models.transaction_item
# import app.models.transaction_item_add_on
# import app.models.stock_transfer
# import app.models.global_setting
# import app.models.outlet_setting


from app.core.config import settings

# Pastikan nama variabel DATABASE_ASYNC_URL di settings.py sudah benar
DATABASE_URL = settings.DATABASE_ASYNC_URL

# Inisialisasi AsyncEngine
# echo=True akan menampilkan semua query SQL di konsol, berguna untuk debugging
engine = create_async_engine(DATABASE_URL, echo=True)

# Fungsi untuk mendapatkan sesi database (digunakan oleh dependensi FastAPI)
async def get_db():
    async_session = AsyncSession(engine, expire_on_commit=False)
    async with async_session as session:
        try:
            yield session
        finally:
            await session.close()