import uuid
from sqlalchemy import (
    Column, Integer, String, Float, Text, ForeignKey, DateTime, Boolean, CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from .database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), default="pending")
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("User", back_populates="organization")
    outlets = relationship("Outlet", back_populates="organization")
    products = relationship("Product", back_populates="organization")
    suppliers = relationship("Supplier", back_populates="organization")
    customers = relationship("Customer", back_populates="organization")
    purchases = relationship("Purchase", back_populates="organization")
    sales = relationship("Sale", back_populates="organization")
    payments = relationship("Payment", back_populates="organization")
    cashier_shifts = relationship("CashierShift", back_populates="organization")
    licenses = relationship("License", back_populates="organization")
    categories = relationship("Category", back_populates="organization")
    cashier_stations = relationship("CashierStation", back_populates="organization")


class License(Base):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    license_key = Column(String(255), unique=True, nullable=False)
    system_id = Column(String(255), unique=True, nullable=False)  # To prevent reuse
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    organization = relationship("Organization", back_populates="licenses")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=False)

    def verify_password(self, password: str) -> bool:
        from .auth import verify_password
        return verify_password(password, self.password)
    role = Column(String(50), default="cashier")
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sales = relationship("Sale", back_populates="user")
    logs = relationship("UserActivityLog", back_populates="user")
    outlet = relationship("Outlet", back_populates="users")
    cashier_shifts = relationship("CashierShift", back_populates="user")
    organization = relationship("Organization", back_populates="users")


class Outlet(Base):
    __tablename__ = "outlets"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    email = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    cashier_stations = relationship("CashierStation", back_populates="outlet")
    printer_settings = relationship("PrinterSettings", back_populates="outlet")
    invoice_templates = relationship("InvoiceTemplate", back_populates="outlet")
    sales = relationship("Sale", back_populates="outlet")
    users = relationship("User", back_populates="outlet")
    cashier_shifts = relationship("CashierShift", back_populates="outlet")
    purchases = relationship("Purchase", back_populates="outlet")
    organization = relationship("Organization", back_populates="outlets")


class CashierStation(Base):
    __tablename__ = "cashier_stations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    outlet_id = Column(Integer, ForeignKey("outlets.id"))
    name = Column(String(100), nullable=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    outlet = relationship("Outlet", back_populates="cashier_stations")
    sales = relationship("Sale", back_populates="cashier_station")
    cashier_shifts = relationship("CashierShift", back_populates="cashier_station")
    organization = relationship("Organization", back_populates="cashier_stations")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    products = relationship("Product", back_populates="category")
    organization = relationship("Organization", back_populates="categories")


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    symbol = Column(String(10))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    products = relationship("Product", back_populates="unit")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    unit_id = Column(Integer, ForeignKey("units.id"))
    name = Column(String(255), nullable=False)
    barcode = Column(String(100), unique=True)
    cost_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    profit_margin = Column(Float)
    stock_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=0)
    description = Column(Text)
    shelf_no = Column(String(50))
    tax_rate = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("Category", back_populates="products")
    unit = relationship("Unit", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")
    purchase_items = relationship("PurchaseItem", back_populates="product")
    organization = relationship("Organization", back_populates="products")



    @validates('stock_quantity')
    def validate_stock_quantity(self, key, value):
        if value < 0:
            raise ValueError("Stock quantity cannot be negative")
        return value

    @hybrid_property
    def profit_margin_calc(self):
        if self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0.0

    @hybrid_property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level

    def update_stock(self, quantity_change):
        """Update stock quantity, e.g., after sale or purchase."""
        self.stock_quantity += quantity_change
        if self.stock_quantity < 0:
            raise ValueError("Insufficient stock")

    def calculate_profit(self, quantity_sold):
        """Calculate profit for a given quantity sold."""
        return (self.selling_price - self.cost_price) * quantity_sold


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sales = relationship("Sale", back_populates="customer")
    organization = relationship("Organization", back_populates="customers")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    purchases = relationship("Purchase", back_populates="supplier")
    organization = relationship("Organization", back_populates="suppliers")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=True)
    total_amount = Column(Float, nullable=False)
    payment_status = Column(String(50), default="pending")
    invoice_number = Column(String(100), unique=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    supplier = relationship("Supplier", back_populates="purchases")
    outlet = relationship("Outlet", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase")
    organization = relationship("Organization", back_populates="purchases")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    cost_price = Column(Float, nullable=False)
    markup_percentage = Column(Float, default=0.0)
    selling_price = Column(Float, nullable=True)
    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    outlet_id = Column(Integer, ForeignKey("outlets.id"))
    cashier_station_id = Column(Integer, ForeignKey("cashier_stations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    total_amount = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    payment_status = Column(String(50), default="paid")
    sale_type = Column(String(50), default="cash")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    outlet = relationship("Outlet", back_populates="sales")
    cashier_station = relationship("CashierStation", back_populates="sales")
    user = relationship("User", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale")
    sale_payments = relationship("SalePayment", back_populates="sale")
    organization = relationship("Organization", back_populates="sales")

    @hybrid_property
    def net_total(self):
        return self.total_amount + self.tax - self.discount

    def calculate_total(self):
        """Calculate total from items."""
        total = sum(item.quantity * item.selling_price for item in self.items)
        self.total_amount = total
        return total

    def apply_discount(self, discount_amount):
        """Apply discount to the sale."""
        if discount_amount > self.total_amount:
            raise ValueError("Discount cannot exceed total amount")
        self.discount = discount_amount
        self.total_amount -= discount_amount

    def add_tax(self, tax_rate):
        """Add tax to the sale."""
        self.tax = self.total_amount * (tax_rate / 100)
        self.total_amount += self.tax


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    selling_price = Column(Float, nullable=False)
    cost_price = Column(Float)
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")

    @hybrid_property
    def total(self):
        return self.quantity * self.selling_price

    @hybrid_property
    def profit(self):
        if self.cost_price:
            return self.quantity * (self.selling_price - self.cost_price)
        return 0.0


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    payment_ref = Column(String(100), unique=True)
    related_type = Column(String(50))
    related_id = Column(Integer)
    amount = Column(Float, nullable=False)
    amount_tendered = Column(Float, nullable=True)
    change = Column(Float, nullable=True)
    method = Column(String(50))
    user_id = Column(Integer, ForeignKey("users.id"))
    outlet_id = Column(Integer, ForeignKey("outlets.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sale_payments = relationship("SalePayment", back_populates="payment")
    organization = relationship("Organization", back_populates="payments")


class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity = Column(Text, nullable=False)
    ip_address = Column(String(100))
    device_info = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="logs")

    @classmethod
    def log_activity(cls, db_session, user_id, activity, ip_address=None, device_info=None):
        """Class method to log user activity."""
        log = cls(
            user_id=user_id,
            activity=activity,
            ip_address=ip_address,
            device_info=device_info
        )
        db_session.add(log)
        db_session.commit()
        return log


class PrinterSettings(Base):
    __tablename__ = "printer_settings"

    id = Column(Integer, primary_key=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"))
    printer_type = Column(String(50), nullable=False)  # thermal or a4
    printer_name = Column(String(255), nullable=False)
    is_default = Column(Boolean, default=False)
    settings = Column(Text)  # JSON string for printer-specific configs
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    outlet = relationship("Outlet", back_populates="printer_settings")


class InvoiceTemplate(Base):
    __tablename__ = "invoice_templates"

    id = Column(Integer, primary_key=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"))
    name = Column(String(255), nullable=False)
    header_text = Column(Text)
    footer_text = Column(Text)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    outlet = relationship("Outlet", back_populates="invoice_templates")


class SalePayment(Base):
    __tablename__ = "sale_payments"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    payment_id = Column(Integer, ForeignKey("payments.id"))
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sale = relationship("Sale", back_populates="sale_payments")
    payment = relationship("Payment", back_populates="sale_payments")


class CashierShift(Base):
    __tablename__ = "cashier_shifts"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    cashier_station_id = Column(Integer, ForeignKey("cashier_stations.id"))
    outlet_id = Column(Integer, ForeignKey("outlets.id"))
    opening_balance = Column(Float, nullable=False)
    closing_balance = Column(Float)
    status = Column(String(50), default="open")
    notes = Column(Text)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))

    user = relationship("User", back_populates="cashier_shifts")
    cashier_station = relationship("CashierStation", back_populates="cashier_shifts")
    outlet = relationship("Outlet", back_populates="cashier_shifts")
    organization = relationship("Organization", back_populates="cashier_shifts")
