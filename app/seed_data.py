# app/seed_data.py

import os
import sys
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Tambahkan root proyek ke sys.path
# Ini memastikan Python dapat menemukan 'app' sebagai package top-level
current_dir = os.path.dirname(os.path.abspath(__file__))
# Naik satu level dari 'app' ke root proyek 'dwc_pos'
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

# --- Setelah baris sys.path.insert, baru impor-impor lainnya ---
from app.db.connection import engine, get_db
from app.db.base import Base
from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission # Pastikan ini diimpor
from app.models.company import Company
from app.models.outlet import Outlet
from app.core.security import get_password_hash # Pastikan path ini benar untuk fungsi hashing password Anda

async def create_initial_data():
    async for session in get_db(): # Menggunakan generator get_db
        try:
            print("Starting data seeding process...")

            # --- Seed Companies ---
            existing_company = await session.execute(select(Company).filter_by(name="Default Company"))
            if not existing_company.scalar_one_or_none():
                print("Creating Default Company...")
                default_company = Company(
                    name="Default Company",
                    address="Jl. Raya Utama No. 123",
                    phone_number="08123456789",
                    email="info@default.com",
                    is_active=True
                )
                session.add(default_company)
                await session.flush() # Penting untuk mendapatkan ID perusahaan

            # Dapatkan company_id setelah flush atau jika sudah ada
            default_company_obj = await session.execute(select(Company).filter_by(name="Default Company"))
            default_company_obj = default_company_obj.scalar_one()


            # --- Seed Outlets ---
            existing_outlet = await session.execute(select(Outlet).filter_by(name="Main Outlet"))
            if not existing_outlet.scalar_one_or_none():
                print("Creating Main Outlet...")
                default_outlet = Outlet(
                    company_id=default_company_obj.id,
                    name="Main Outlet",
                    address="Jl. Cabang No. 1",
                    phone_number="08123456780",
                    email="outlet@default.com",
                    is_active=True
                )
                session.add(default_outlet)
                await session.flush() # Penting untuk mendapatkan ID outlet

            # Dapatkan outlet_id setelah flush atau jika sudah ada
            default_outlet_obj = await session.execute(select(Outlet).filter_by(name="Main Outlet"))
            default_outlet_obj = default_outlet_obj.scalar_one()


            # --- Seed Roles ---
            admin_role = await session.execute(select(Role).filter_by(name="admin"))
            admin_role_obj = admin_role.scalar_one_or_none()
            if not admin_role_obj:
                print("Creating 'admin' role...")
                admin_role_obj = Role(name="admin", description="Administrator role", is_active=True)
                session.add(admin_role_obj)
                await session.flush() # Penting untuk mendapatkan ID

            staff_role = await session.execute(select(Role).filter_by(name="staff"))
            staff_role_obj = staff_role.scalar_one_or_none()
            if not staff_role_obj:
                print("Creating 'staff' role...")
                staff_role_obj = Role(name="staff", description="Staff role", is_active=True)
                session.add(staff_role_obj)
                await session.flush()


            # --- Seed Permissions ---
            create_user_perm = await session.execute(select(Permission).filter_by(name="create_user"))
            create_user_perm_obj = create_user_perm.scalar_one_or_none()
            if not create_user_perm_obj:
                print("Creating 'create_user' permission...")
                create_user_perm_obj = Permission(name="create_user", description="Allows creating new users")
                session.add(create_user_perm_obj)
                await session.flush()

            view_users_perm = await session.execute(select(Permission).filter_by(name="view_users"))
            view_users_perm_obj = view_users_perm.scalar_one_or_none()
            if not view_users_perm_obj:
                print("Creating 'view_users' permission...")
                view_users_perm_obj = Permission(name="view_users", description="Allows viewing users list")
                session.add(view_users_perm_obj)
                await session.flush()

            # --- Connect Roles and Permissions (RolePermission Table) ---
            print("Connecting roles and permissions...")
            # Admin role gets create_user and view_users permissions
            for perm_obj in [create_user_perm_obj, view_users_perm_obj]:
                if perm_obj: # Only add if permission was created/found
                    existing_rp = await session.execute(
                        select(RolePermission).filter_by(
                            role_id=admin_role_obj.id,
                            permission_id=perm_obj.id
                        )
                    )
                    if not existing_rp.scalar_one_or_none():
                        rp = RolePermission(role_id=admin_role_obj.id, permission_id=perm_obj.id)
                        session.add(rp)
                        print(f"  Added permission '{perm_obj.name}' to role '{admin_role_obj.name}'")

            # --- Seed Superadmin User ---
            superadmin_user = await session.execute(select(User).filter_by(email="superadmin@example.com"))
            superadmin_user_obj = superadmin_user.scalar_one_or_none()

            if not superadmin_user_obj:
                print("Creating superadmin user...")
                hashed_password = get_password_hash("supersecretpassword") # Ganti dengan password yang kuat

                superadmin_user_obj = User(
                    username="superadmin",
                    email="superadmin@example.com",
                    hashed_password=hashed_password,
                    full_name="Super Administrator",
                    phone_number="08111222333",
                    pin="1234", # Contoh PIN, sesuaikan jika perlu hashing
                    is_active=True,
                    email_verified=True,
                    access_type="GLOBAL", # Sesuaikan dengan Enum jika perlu
                    outlet_id=None # Superadmin biasanya GLOBAL, tidak terikat outlet
                )
                session.add(superadmin_user_obj)
                await session.flush() # Penting untuk mendapatkan ID

            # --- Connect Superadmin to Admin Role (UserRole Table) ---
            print("Connecting superadmin user to admin role...")
            existing_ur = await session.execute(
                select(UserRole).filter_by(
                    user_id=superadmin_user_obj.id,
                    role_id=admin_role_obj.id
                )
            )
            if not existing_ur.scalar_one_or_none():
                ur = UserRole(user_id=superadmin_user_obj.id, role_id=admin_role_obj.id)
                session.add(ur)
                print(f"  Connected user '{superadmin_user_obj.username}' to role '{admin_role_obj.name}'")

            # Commit semua perubahan ke database
            await session.commit()
            print("Initial data created/updated successfully!")

        except Exception as e:
            await session.rollback()
            print(f"Error seeding data: {e}")
            raise # Re-raise the exception to see full traceback for debugging

# Jalankan fungsi async
if __name__ == "__main__":
    asyncio.run(create_initial_data())