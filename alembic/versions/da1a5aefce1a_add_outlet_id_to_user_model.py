"""Add outlet_id to User model

Revision ID: da1a5aefce1a
Revises: 66ef8b1a6c1d
Create Date: 2025-07-04 16:13:17.699756

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect # Pastikan ini diimpor!

# revision identifiers, used by Alembic.
revision: str = 'da1a5aefce1a'
down_revision: Union[str, Sequence[str], None] = '66ef8b1a6c1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Dapatkan objek bind untuk menginspeksi database
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    # Ambil daftar kolom dan foreign keys di tabel 'users' untuk pemeriksaan
    user_columns = [col['name'] for col in inspector.get_columns('users')]
    user_constraints = inspector.get_foreign_keys('users')
    user_fk_names = [fk['name'] for fk in user_constraints]
    
    # Ambil daftar kolom di tabel 'companies'
    company_columns = [col['name'] for col in inspector.get_columns('companies')]


    # --- Perubahan pada tabel 'companies' ---
    op.alter_column('companies', 'address',
                   existing_type=sa.TEXT(),
                   type_=sa.String(),
                   existing_nullable=True)
    op.alter_column('companies', 'created_at',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.DateTime(timezone=True),
                   nullable=False,
                   existing_server_default=sa.text('now()'))
    op.alter_column('companies', 'updated_at',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.DateTime(timezone=True),
                   nullable=False,
                   existing_server_default=sa.text('now()'))
    op.alter_column('companies', 'deleted_at',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.DateTime(timezone=True),
                   existing_nullable=True)
    
    # Tambahkan unique constraint 'uq_companies_email' jika belum ada
    # Kita berikan nama eksplisit agar mudah di-drop di downgrade
    unique_email_constraint_name = 'uq_companies_email'
    existing_unique_constraints = inspector.get_unique_constraints('companies')
    
    constraint_exists_for_email = False
    for const in existing_unique_constraints:
        if const['column_names'] == ['email']:
            constraint_exists_for_email = True
            break
            
    if not constraint_exists_for_email:
        op.create_unique_constraint(unique_email_constraint_name, 'companies', ['email'])


    # --- Penanganan Kolom 'is_superuser' di tabel 'users' ---
    if 'is_superuser' not in user_columns:
        op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=True, server_default=sa.text('FALSE')))
        op.execute(
            sa.text("UPDATE users SET is_superuser = FALSE WHERE is_superuser IS NULL")
        )
        op.alter_column('users', 'is_superuser',
                       existing_type=sa.Boolean(),
                       nullable=False,
                       existing_server_default=sa.text('FALSE'))
    else:
        op.alter_column('users', 'is_superuser',
                       existing_type=sa.Boolean(),
                       nullable=False,
                       existing_server_default=sa.text('FALSE'))


    # --- Tambahkan kolom 'company_id' dan 'outlet_id' ke tabel 'users' ---
    if 'company_id' not in user_columns:
        op.add_column('users', sa.Column('company_id', sa.Integer(), nullable=True))

    if 'outlet_id' not in user_columns:
        op.add_column('users', sa.Column('outlet_id', sa.Integer(), nullable=True))


    # --- Perbarui kolom lain di 'users' ---
    op.alter_column('users', 'full_name',
                   existing_type=sa.VARCHAR(length=255),
                   nullable=True)
    op.alter_column('users', 'created_at',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.DateTime(timezone=True),
                   nullable=False,
                   existing_server_default=sa.text('now()'))
    op.alter_column('users', 'updated_at',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.DateTime(timezone=True),
                   nullable=False,
                   existing_server_default=sa.text('now()'))
    op.alter_column('users', 'deleted_at',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.DateTime(timezone=True),
                   existing_nullable=True)


    # --- Buat Foreign Keys ---
    fk_company_name = op.f('fk_users_company_id_companies')
    if fk_company_name not in user_fk_names:
        op.create_foreign_key(fk_company_name, 'users', 'companies', ['company_id'], ['id'])
    
    fk_outlet_name = op.f('fk_users_outlet_id_outlets')
    if fk_outlet_name not in user_fk_names:
        op.create_foreign_key(fk_outlet_name, 'users', 'outlets', ['outlet_id'], ['id'])


    # --- Drop Kolom Lama yang Tidak Dibutuhkan Lagi (dan menyebabkan NotNullViolationError) ---
    # Jika kolom-kolom ini tidak lagi ada di model User Python Anda, mereka perlu dihapus dari DB.
    if 'access_type' in user_columns:
        op.drop_column('users', 'access_type')
    
    if 'pin' in user_columns:
        op.drop_column('users', 'pin')
    if 'email_verified' in user_columns:
        op.drop_column('users', 'email_verified')
    if 'phone_number' in user_columns:
        op.drop_column('users', 'phone_number')


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_columns = [col['name'] for col in inspector.get_columns('users')]
    user_constraints = inspector.get_foreign_keys('users')
    user_fk_names = [fk['name'] for fk in user_constraints]
    company_columns = [col['name'] for col in inspector.get_columns('companies')]

    # --- Tambahkan kembali kolom-kolom yang DIdrop di upgrade() ---
    # Ini harus sesuai dengan apa yang Anda drop di upgrade().
    if 'phone_number' not in user_columns:
        op.add_column('users', sa.Column('phone_number', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    
    if 'access_type' not in user_columns:
        # Asumsi: ENUM 'useraccesstype' sudah ada dari migrasi sebelumnya
        # Jika tidak, Anda mungkin perlu membuat ENUM ini di sini sebelum add_column:
        # postgresql.ENUM('GLOBAL', 'OUTLET_SPECIFIC', name='useraccesstype', create_type=True).create(op.get_bind())
        op.add_column('users', sa.Column('access_type', postgresql.ENUM('GLOBAL', 'OUTLET_SPECIFIC', name='useraccesstype'), autoincrement=False, nullable=False))
        
    if 'email_verified' not in user_columns:
        op.add_column('users', sa.Column('email_verified', sa.BOOLEAN(), autoincrement=False, nullable=True))
    if 'pin' not in user_columns:
        op.add_column('users', sa.Column('pin', sa.VARCHAR(length=255), autoincrement=False, nullable=True))


    # --- Hapus Foreign Keys ---
    fk_outlet_name = op.f('fk_users_outlet_id_outlets')
    if fk_outlet_name in user_fk_names:
        op.drop_constraint(fk_outlet_name, 'users', type_='foreignkey')
    
    fk_company_name = op.f('fk_users_company_id_companies')
    if fk_company_name in user_fk_names:
        op.drop_constraint(fk_company_name, 'users', type_='foreignkey')
    
    # --- Hapus kolom yang ditambahkan di upgrade ---
    if 'outlet_id' in user_columns:
        op.drop_column('users', 'outlet_id')
    if 'company_id' in user_columns:
        op.drop_column('users', 'company_id')
    
    # --- Kembalikan is_superuser ke keadaan semula ---
    if 'is_superuser' in user_columns:
        op.drop_column('users', 'is_superuser')
        # Jika is_superuser awalnya memang ada tapi nullable=True, Anda bisa tambahkan kembali:
        # op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=True))


    # Perubahan pada tabel 'users' (sesuai autogenerate awal)
    op.alter_column('users', 'deleted_at',
                   existing_type=sa.DateTime(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   existing_nullable=True)
    op.alter_column('users', 'updated_at',
                   existing_type=sa.DateTime(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   nullable=True,
                   existing_server_default=sa.text('now()'))
    op.alter_column('users', 'created_at',
                   existing_type=sa.DateTime(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   nullable=True,
                   existing_server_default=sa.text('now()'))
    op.alter_column('users', 'full_name',
                   existing_type=sa.VARCHAR(length=255),
                   nullable=False)

    # --- Hapus Unique Constraint 'companies_email' ---
    # Gunakan nama eksplisit yang kita definisikan di upgrade()
    unique_email_constraint_name = 'uq_companies_email'
    existing_unique_constraints = inspector.get_unique_constraints('companies')
    
    constraint_exists_to_drop = False
    for const in existing_unique_constraints:
        # Cek apakah constraint yang kita buat di upgrade ada, atau constraint yang auto-generated dengan kolom yang sama
        if const['name'] == unique_email_constraint_name or (const['column_names'] == ['email'] and const['name'] is not None):
            constraint_exists_to_drop = True
            # Jika namanya berbeda tapi untuk kolom email, gunakan nama yang ada di DB
            if const['name'] != unique_email_constraint_name and const['name'] is not None:
                unique_email_constraint_name = const['name']
            break
            
    if constraint_exists_to_drop:
        op.drop_constraint(unique_email_constraint_name, 'companies', type_='unique')

    # Perubahan pada tabel 'companies' (lanjutan autogenerate awal)
    op.alter_column('companies', 'deleted_at',
                   existing_type=sa.DateTime(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   existing_nullable=True)
    op.alter_column('companies', 'updated_at',
                   existing_type=sa.DateTime(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   nullable=True,
                   existing_server_default=sa.text('now()'))
    op.alter_column('companies', 'created_at',
                   existing_type=sa.DateTime(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   nullable=True,
                   existing_server_default=sa.text('now()'))
    op.alter_column('companies', 'address',
                   existing_type=sa.String(),
                   type_=sa.TEXT(),
                   existing_nullable=True)