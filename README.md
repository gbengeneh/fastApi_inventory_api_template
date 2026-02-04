# Inventory POS System

A comprehensive FastAPI-based Point of Sale (POS) system designed for inventory management, sales tracking, and retail operations. The system supports both online and offline modes with automatic data synchronization.

## 🚀 Features

### Core Functionality
- **Multi-Organization Support**: Manage multiple organizations with separate data isolation
- **User Management**: Role-based access control (Admin, Manager, Cashier)
- **Outlet Management**: Support for multiple store locations
- **Product Management**: Comprehensive product catalog with categories, units, and stock tracking
- **Sales Processing**: Complete POS functionality with receipt generation
- **Purchase Management**: Track supplier purchases and inventory replenishment
- **Payment Processing**: Multiple payment methods (cash, card, bank transfer, credit)
- **Cashier Shifts**: Track cashier sessions with opening/closing balances
- **License Management**: Software licensing system for organizations

### Advanced Features
- **Offline/Online Sync**: Automatic data synchronization with central database
- **Printer Integration**: Thermal and A4 receipt/invoice printing
- **Invoice Templates**: Customizable invoice layouts
- **Activity Logging**: Comprehensive user activity tracking
- **Stock Alerts**: Automatic low stock notifications
- **Barcode Support**: Product barcode scanning
- **Tax Calculation**: Configurable tax rates per product
- **Discount Management**: Sale-level and item-level discounts

## 🛠 Tech Stack

### Backend
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Local database (development/production)
- **PostgreSQL**: Central database for multi-location sync
- **Supabase**: Cloud database fallback for sync operations
- **Alembic**: Database migrations
- **Pydantic**: Data validation and serialization

### Authentication & Security
- **JWT Tokens**: Access and refresh token authentication
- **bcrypt**: Password hashing
- **Role-based Access Control**: Admin, Manager, Cashier roles

### Additional Libraries
- **APScheduler**: Background task scheduling for sync
- **ReportLab**: PDF generation for invoices
- **win32print/win32api**: Windows printer integration
- **python-jose**: JWT token handling
- **python-multipart**: File upload handling

## 📋 Prerequisites

- Python 3.8+
- SQLite (built-in with Python)
- PostgreSQL (optional, for central database)
- Windows OS (for printer integration)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd inventorypadi/inventory_api
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Local SQLite Database
The application automatically creates a local SQLite database (`inventory.db`) on first run.

#### Central PostgreSQL Database (Optional)
For multi-location setups, configure PostgreSQL in `app/database.py`:
```python
POSTGRESQL_DATABASE_URL = "postgresql://username:password@host:port/database"
```

#### Supabase Setup (Optional)
Configure Supabase credentials in `app/database.py`:
```python
SUPABASE_URL = "your-supabase-url"
SUPABASE_ANON_KEY = "your-supabase-anon-key"
```

### 5. Run Database Migrations
```bash
alembic upgrade head
```

### 6. Seed Initial Data
```bash
python seed_data.py
```

This creates:
- Default organization
- Sample categories (Provision, Kitchen, Toiletries, Gifts, Frozen)
- Sample units (Piece, Kilogram, Liter, Pack, Box)
- Sample products (50+ items across categories)
- Default outlet and supplier
- Admin user (email: `admin@inventory.com`, password: `admin123`)

### 7. Start the Application
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

### Interactive API Docs
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Endpoints Overview
See [API_ENDPOINTS.md](API_ENDPOINTS.md) for detailed endpoint documentation.

### Authentication
The API uses JWT token authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

#### Login Example
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@inventory.com&password=admin123"
```

## 🗄 Database Models

### Core Models
- **Organization**: Multi-tenant organization management
- **License**: Software licensing per organization
- **User**: Staff members with role-based access
- **Outlet**: Store locations
- **CashierStation**: POS terminals within outlets
- **Category**: Product categorization
- **Unit**: Measurement units (kg, L, pc, etc.)
- **Product**: Inventory items with stock tracking
- **Supplier**: Vendor management
- **Purchase/PurchaseItem**: Procurement tracking
- **Sale/SaleItem**: Transaction management
- **Payment**: Payment processing
- **CashierShift**: Shift management
- **PrinterSettings/InvoiceTemplate**: Printing configuration
- **UserActivityLog**: Audit trail

### Key Relationships
- Organization → Users, Outlets, Products, Sales, etc.
- Outlet → Users, Sales, CashierStations
- Product → Category, Unit, SaleItems, PurchaseItems
- Sale → SaleItems, Payments, User, Outlet
- Purchase → PurchaseItems, Supplier

## 🔄 Sync Functionality

The system supports automatic synchronization between local and central databases:

### Sync Process
1. **Local SQLite**: Primary database for fast operations
2. **Central PostgreSQL/Supabase**: Backup and multi-location sync
3. **Automatic Sync**: Runs every 30 minutes via APScheduler
4. **Offline Mode**: Continues operation when central DB is unavailable

### Sync Tables (in order)
1. Organizations
2. Outlets
3. Users
4. Licenses
5. Categories & Units
6. Suppliers
7. Products
8. Purchases & PurchaseItems
9. Sales & SaleItems
10. Payments
11. Activity Logs, Printer Settings, etc.

## 🧪 Testing

### Run Tests
```bash
pytest
```

### Test Structure
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Database Tests**: Model and relationship testing

### Test Database
Tests use a separate test database (`test_inventory.db`) to avoid affecting production data.

## 🖨️ Printing Integration

### Supported Printers
- **Thermal Printers**: Receipt printing
- **A4 Printers**: Invoice printing via PDF

### Features
- **Custom Templates**: Header/footer customization
- **Multiple Formats**: Text receipts, PDF invoices
- **Printer Detection**: Automatic printer discovery
- **Fallback Printing**: PDF generation when direct printing fails

### Configuration
Printer settings are managed per outlet with default templates.

## 🚀 Deployment

### Production Deployment
1. Set environment variables for database URLs and secrets
2. Use a production ASGI server (e.g., Gunicorn + Uvicorn)
3. Configure reverse proxy (nginx)
4. Set up SSL certificates
5. Configure log rotation

### Docker Deployment (Recommended)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN alembic upgrade head

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///./inventory.db
CENTRAL_DATABASE_URL=postgresql://user:pass@host:port/db

# Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=3000

# Supabase (optional)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

### Key Settings
- **Sync Interval**: Configurable sync frequency (default: 30 minutes)
- **Token Expiry**: JWT token lifetimes
- **Database Connections**: Connection pooling settings
- **Printer Settings**: Per-outlet printer configuration

## 📊 Monitoring & Logging

### Logging
- **Application Logs**: FastAPI request/response logging
- **Sync Logs**: Data synchronization status
- **Error Logs**: Exception tracking
- **Activity Logs**: User action auditing

### Health Checks
- Database connectivity
- Sync status
- Printer availability
- API endpoint health

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure all tests pass
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation for new features
- Use type hints for better code clarity

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the existing issues
- Create a new issue for bugs or feature requests

## 🔄 Version History

### v1.0.0
- Initial release
- Core POS functionality
- Multi-organization support
- Offline/online sync
- Printer integration
- Comprehensive API

---

**Note**: This documentation is comprehensive but may need updates as the application evolves. Please check the latest version for any changes.
