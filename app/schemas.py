from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import datetime
import re


# ---------- ORGANIZATION SCHEMAS ----------

class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    email: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
            raise ValueError('Invalid email format')
        return v


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


class OrganizationResponse(OrganizationBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- LICENSE SCHEMAS ----------

class LicenseBase(BaseModel):
    license_key: str = Field(..., min_length=1, max_length=255)
    system_id: str = Field(..., min_length=1, max_length=255)
    expires_at: datetime


class LicenseCreate(LicenseBase):
    pass


class LicenseUpdate(BaseModel):
    license_key: Optional[str] = Field(None, min_length=1, max_length=255)
    system_id: Optional[str] = Field(None, min_length=1, max_length=255)
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class LicenseResponse(LicenseBase):
    id: int
    organization_id: str
    issued_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# ---------- BASIC SCHEMAS ----------

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    role: str = Field("cashier", pattern=r'^(admin|manager|cashier)$')
    status: str = Field("active", pattern=r'^(active|inactive|suspended)$')
    outlet_id: int

    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
            raise ValueError('Invalid email format')
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72)
    outlet_id: Optional[int] = None

class UserLogin(BaseModel):
    email: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    role: Optional[str] = Field(None, pattern=r'^(admin|manager|cashier)$')
    status: Optional[str] = Field(None, pattern=r'^(active|inactive|suspended)$')


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class OutletBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

    @validator('email')
    def validate_email(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
            raise ValueError('Invalid email format')
        return v


class OutletCreate(OutletBase):
    pass


class OutletUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


class OutletResponse(OutletBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CashierStationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    outlet_id: int
    status: str = Field("active", pattern=r'^(active|inactive)$')


class CashierStationCreate(CashierStationBase):
    pass


class CashierStationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = Field(None, pattern=r'^(active|inactive)$')


class CashierStationResponse(CashierStationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UnitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    symbol: Optional[str] = Field(None, max_length=10)


class UnitCreate(UnitBase):
    pass


class UnitUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    symbol: Optional[str] = Field(None, max_length=10)


class UnitResponse(UnitBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category_id: int
    unit_id: int
    barcode: Optional[str] = Field(None, max_length=100)
    cost_price: float = Field(..., gt=0)
    selling_price: float = Field(..., gt=0)
    stock_quantity: int = Field(0, ge=0)
    reorder_level: int = Field(0, ge=0)
    description: Optional[str] = None
    shelf_no: Optional[str] = Field(None, max_length=50)
    tax_rate: float = Field(0.0, ge=0, le=1)

    @validator('barcode')
    def validate_barcode(cls, v):
        if v == '':
            return None
        return v


class ProductCreate(ProductBase):
    pass


class ProductBulkCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category_id: int
    unit_id: int
    barcode: Optional[str] = Field(None, max_length=100)
    cost_price: float = Field(..., gt=0)
    selling_price: float = Field(..., gt=0)
    stock_quantity: int = Field(0, ge=0)
    reorder_level: int = Field(0, ge=0)
    description: Optional[str] = None
    shelf_no: Optional[str] = Field(None, max_length=50)
    tax_rate: Optional[float] = Field(None, ge=0, le=1)  # Decimal 0-1, optional

    @validator('barcode')
    def validate_barcode(cls, v):
        if v == '':
            return None
        return v

    @validator('selling_price')
    def validate_selling_price(cls, v, values):
        if 'cost_price' in values and v <= values['cost_price']:
            raise ValueError('Selling price must be greater than cost price')
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category_id: Optional[int] = None
    unit_id: Optional[int] = None
    barcode: Optional[str] = Field(None, max_length=100)
    cost_price: Optional[float] = Field(None, gt=0)
    selling_price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    shelf_no: Optional[str] = Field(None, max_length=50)
    tax_rate: Optional[float] = Field(None, ge=0, le=1)

    @validator('barcode')
    def validate_barcode(cls, v):
        if v == '':
            return None
        return v


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    profit_margin: Optional[float] = None

    class Config:
        from_attributes = True


class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    address: Optional[str] = None

    @validator('email')
    def validate_email(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
            raise ValueError('Invalid email format')
        return v


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    address: Optional[str] = None


class SupplierResponse(SupplierBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., pattern=r'^\+?[\d\s\-\(\)]+$')
    address: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    address: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: int
    organization_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    cost_price: float = Field(..., gt=0)
    markup_percentage: float = Field(0.0, ge=0)
    selling_price: Optional[float] = Field(None, gt=0)


class PurchaseItemCreate(PurchaseItemBase):
    pass


class PurchaseItemUpdate(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[int] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)
    markup_percentage: Optional[float] = Field(None, ge=0)
    selling_price: Optional[float] = Field(None, gt=0)


class PurchaseItemResponse(PurchaseItemBase):
    id: int
    purchase_id: int

    class Config:
        from_attributes = True


class PurchaseBase(BaseModel):
    supplier_id: Optional[int] = None
    outlet_id: Optional[int] = None
    total_amount: float = Field(..., ge=0)
    payment_status: str = Field("pending", pattern=r'^(pending|paid|partial)$')
    invoice_number: Optional[str] = Field(None, max_length=100)


class PurchaseCreate(PurchaseBase):
    items: List[PurchaseItemCreate]
    created_by: Optional[int] = None


class PurchaseUpdate(BaseModel):
    supplier_id: Optional[int] = None
    outlet_id: Optional[int] = None
    total_amount: Optional[float] = Field(None, ge=0)
    payment_status: Optional[str] = Field(None, pattern=r'^(pending|paid|partial)$')
    invoice_number: Optional[str] = Field(None, max_length=100)


class PurchaseResponse(PurchaseBase):
    id: int
    created_by: int
    created_at: datetime
    items: List[PurchaseItemResponse]

    class Config:
        from_attributes = True


class SaleItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    selling_price: float = Field(..., gt=0)
    cost_price: Optional[float] = Field(None, gt=0)


class SaleItemCreate(SaleItemBase):
    pass


class SaleItemUpdate(BaseModel):
    product_id: Optional[int] = None
    quantity: Optional[int] = Field(None, gt=0)
    selling_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, gt=0)


class SaleItemResponse(SaleItemBase):
    id: int
    sale_id: int
    total: Optional[float] = None

    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    outlet_id: int
    cashier_station_id: Optional[int] = None
    user_id: int
    customer_id: Optional[int] = None
    payment_id: Optional[int] = None
    total_amount: float = Field(..., ge=0)
    discount: float = Field(0.0, ge=0)
    tax: float = Field(0.0, ge=0)
    payment_status: str = Field("paid", pattern=r'^(paid|pending|refunded)$')
    sale_type: str = Field("cash", pattern=r'^(cash|card|credit)$')


class SaleCreate(SaleBase):
    cashier_station_id: Optional[int] = None
    items: List[SaleItemCreate]


class SaleUpdate(BaseModel):
    outlet_id: Optional[int] = None
    cashier_station_id: Optional[int] = None
    user_id: Optional[int] = None
    customer_id: Optional[int] = None
    total_amount: Optional[float] = Field(None, ge=0)
    discount: Optional[float] = Field(None, ge=0)
    tax: Optional[float] = Field(None, ge=0)
    payment_status: Optional[str] = Field(None, pattern=r'^(paid|pending|refunded)$')
    sale_type: Optional[str] = Field(None, pattern=r'^(cash|card|credit)$')


class SalePaymentBase(BaseModel):
    sale_id: int
    payment_id: int
    amount: float = Field(..., gt=0)


class SalePaymentCreate(SalePaymentBase):
    pass


class SalePaymentUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)


class SalePaymentResponse(SalePaymentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SaleResponse(SaleBase):
    id: int
    created_at: datetime
    items: List[SaleItemResponse]
    payments: Optional[List[SalePaymentResponse]] = None

    class Config:
        from_attributes = True


class PaymentBase(BaseModel):
    payment_ref: str = Field(..., max_length=100)
    related_type: str = Field(..., pattern=r'^(sale|purchase)$')
    related_id: int
    amount: float = Field(..., gt=0)
    amount_tendered: Optional[float] = Field(None, gt=0)
    change: Optional[float] = Field(None, ge=0)
    method: str = Field(..., pattern=r'^(cash|card|bank_transfer|credit)$')
    user_id: int
    outlet_id: int


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    payment_ref: Optional[str] = Field(None, max_length=100)
    related_type: Optional[str] = Field(None, pattern=r'^(sale|purchase)$')
    related_id: Optional[int] = None
    amount: Optional[float] = Field(None, gt=0)
    amount_tendered: Optional[float] = Field(None, gt=0)
    change: Optional[float] = Field(None, ge=0)
    method: Optional[str] = Field(None, pattern=r'^(cash|card|bank_transfer|credit)$')
    user_id: Optional[int] = None
    outlet_id: Optional[int] = None


class PaymentResponse(PaymentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserActivityLogBase(BaseModel):
    user_id: int
    activity: str = Field(..., min_length=1)
    ip_address: Optional[str] = Field(None, max_length=100)
    device_info: Optional[str] = Field(None, max_length=255)


class UserActivityLogCreate(UserActivityLogBase):
    pass


class UserActivityLogResponse(UserActivityLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PrinterSettingsBase(BaseModel):
    outlet_id: int
    printer_type: str = Field(..., pattern=r'^(thermal|a4)$')
    printer_name: str = Field(..., min_length=1, max_length=255)
    is_default: bool = False
    settings: Optional[str] = None


class PrinterSettingsCreate(PrinterSettingsBase):
    pass


class PrinterSettingsUpdate(BaseModel):
    printer_type: Optional[str] = Field(None, pattern=r'^(thermal|a4)$')
    printer_name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_default: Optional[bool] = None
    settings: Optional[str] = None


class PrinterSettingsResponse(PrinterSettingsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceTemplateBase(BaseModel):
    outlet_id: int
    name: str = Field(..., min_length=1, max_length=255)
    header_text: Optional[str] = None
    footer_text: Optional[str] = None
    is_default: bool = False


class InvoiceTemplateCreate(InvoiceTemplateBase):
    pass


class InvoiceTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    header_text: Optional[str] = None
    footer_text: Optional[str] = None
    is_default: Optional[bool] = None


class InvoiceTemplateResponse(InvoiceTemplateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CashierShiftBase(BaseModel):
    user_id: int
    cashier_station_id: int
    outlet_id: int
    opening_balance: float = Field(..., ge=0)
    closing_balance: Optional[float] = Field(None, ge=0)
    status: str = Field("open", pattern=r'^(open|closed)$')
    notes: Optional[str] = None


class CashierShiftCreate(BaseModel):
    user_id: int
    cashier_station_id: int
    outlet_id: int
    opening_balance: float = Field(..., ge=0)
    notes: Optional[str] = None


class CashierShiftUpdate(BaseModel):
    closing_balance: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern=r'^(open|closed)$')
    notes: Optional[str] = None


class CashierShiftResponse(CashierShiftBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True
