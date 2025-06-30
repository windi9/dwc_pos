# dwc_pos/app/db/base.py

from app.db.connection import Base
# Import all your SQLAlchemy models here so that Base.metadata.create_all can find them
# Example (will be uncommented/added as we create them):
# from app.models.user import User
# from app.models.category import Category
# from app.models.product import Product
# from app.models.customer import Customer
# from app.models.payment_method import PaymentMethod
# from app.models.discount import Discount
# from app.models.order import Order
# from app.models.order_item import OrderItem