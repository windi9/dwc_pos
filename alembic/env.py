# dwc_pos/alembic/env.py

from logging.config import fileConfig
import os
from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# This is the Alembic Config object, which provides
# access to values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Start Alembic's Database URL and Model Setup ---

# Load environment variables from .env file
# Ensure this path is correct relative to where alembic is run (project root)
load_dotenv(os.path.join(os.getcwd(), '.env'))

# Get database URL from environment variable
# This is crucial for Alembic to connect to your database
# Make sure DATABASE_URL is set in your .env file
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Import your Base here
from app.db.base import Base

# --- PENTING: IMPOR SEMUA MODEL ANDA DI SINI ---
# Ini memastikan bahwa semua kelas model yang mewarisi dari Base
# akan dieksekusi dan didaftarkan ke Base.metadata
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


# target_metadata is where we specify all the SQLAlchemy Base
# that Alembic should track for migrations.
target_metadata = Base.metadata

# --- End Alembic's Database URL and Model Setup ---


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configuratidon is for generating SQL scripts without a direct
    database connection.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario, we connect to a database using an URL from the config
    and acquire a connection from a SQLAlchemy Engine.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()