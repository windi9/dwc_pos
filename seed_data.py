# dwc_pos/seed_data.py

import os
import sys

# Tambahkan path proyek Anda ke sys.path agar impor app.X berhasil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from sqlalchemy.orm import Session
from app.db.connection import engine, SessionLocal, Base
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission
from app.core.security import get_password_hash # Jika perlu untuk user awal
from app.core.config import settings

def create_initial_roles_and_permissions(db: Session):
    print("Creating initial roles...")
    
    # Check if roles already exist to prevent duplicates
    roles_data = [
        {"name": "Superadmin", "description": "Full access to all system features"},
        {"name": "Admin", "description": "Manage users and products"},
        {"name": "Employee", "description": "Process sales and manage inventory"},
        {"name": "Customer", "description": "Basic user role for customers"}
    ]

    for role_info in roles_data:
        existing_role = db.query(Role).filter(Role.name == role_info["name"]).first()
        if not existing_role:
            role = Role(name=role_info["name"], description=role_info["description"])
            db.add(role)
            print(f"  - Added role: {role.name}")
    db.commit() # Commit after adding roles to get their IDs

    print("Creating initial permissions...")
    permissions_data = [
        {"name": "create_user", "description": "Allows creating new user accounts"},
        {"name": "read_user", "description": "Allows viewing user details"},
        {"name": "update_user", "description": "Allows updating user accounts"},
        {"name": "delete_user", "description": "Allows deleting user accounts"},
        {"name": "create_product", "description": "Allows adding new products"},
        {"name": "read_product", "description": "Allows viewing product details"},
        {"name": "update_product", "description": "Allows updating product details"},
        {"name": "delete_product", "description": "Allows deleting products"},
        {"name": "process_sale", "description": "Allows processing sales transactions"},
        {"name": "view_sales_report", "description": "Allows viewing sales reports"},
        # Tambahkan permission lain sesuai kebutuhan
    ]

    for perm_info in permissions_data:
        existing_perm = db.query(Permission).filter(Permission.name == perm_info["name"]).first()
        if not existing_perm:
            permission = Permission(name=perm_info["name"], description=perm_info["description"])
            db.add(permission)
            print(f"  - Added permission: {permission.name}")
    db.commit() # Commit after adding permissions to get their IDs

    print("Assigning permissions to roles...")
    superadmin_role = db.query(Role).filter(Role.name == "Superadmin").first()
    all_permissions = db.query(Permission).all()

    if superadmin_role and all_permissions:
        for perm in all_permissions:
            # Check if this permission is already assigned to superadmin
            existing_rp = db.query(RolePermission).filter(
                RolePermission.role_id == superadmin_role.id,
                RolePermission.permission_id == perm.id
            ).first()
            if not existing_rp:
                rp = RolePermission(role_id=superadmin_role.id, permission_id=perm.id)
                db.add(rp)
                print(f"  - Assigned {perm.name} to {superadmin_role.name}")
    db.commit()

    # Optional: Create a superadmin user if one doesn't exist
    print("Creating initial superadmin user (if not exists)...")
    superadmin_user = db.query(User).filter(User.email == "superadmin@example.com").first()
    if not superadmin_user:
        hashed_password = get_password_hash("superadminpassword") # Ganti dengan password yang kuat
        user = User(
            username="superadmin",
            email="superadmin@example.com",
            hashed_password=hashed_password,
            is_active=True,
            email_verified=True,
            full_name="Default Superadmin"
        )
        db.add(user)
        db.flush() # Use flush to get user.id before commit
        
        # Assign Superadmin role to this user
        superadmin_role = db.query(Role).filter(Role.name == "Superadmin").first()
        if superadmin_role:
            user_role = UserRole(user_id=user.id, role_id=superadmin_role.id)
            db.add(user_role)
            print(f"  - Created superadmin user and assigned 'Superadmin' role.")
        else:
            print("  - Superadmin role not found to assign to new user.")
    else:
        print("  - Superadmin user already exists.")
        
    db.commit()
    print("Seeding complete!")

if __name__ == "__main__":
    # Create tables if they don't exist (optional, Alembic handles this better)
    # Base.metadata.create_all(bind=engine)
    
    # Get a database session
    db = SessionLocal()
    try:
        create_initial_roles_and_permissions(db)
    except Exception as e:
        db.rollback()
        print(f"An error occurred during seeding: {e}")
    finally:
        db.close()