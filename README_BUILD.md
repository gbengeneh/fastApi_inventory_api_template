# Inventory Backend - Build Instructions

## Overview
This backend is built with FastAPI and packaged as a standalone executable for easy deployment with Tauri desktop applications.

## Prerequisites
- Python 3.8+
- Virtual environment (recommended)

## Building the Executable

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Build the Executable
```bash
python build_exe.py
```

This will create `inventory_backend.exe` in the `dist/` directory.

## Running the Backend

### Option 1: Using the Batch File
Double-click `run_backend.bat` to start the backend.

### Option 2: Direct Execution
```bash
dist\inventory_backend.exe
```

### Option 3: Development Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### License Management
- `POST /licenses/validate` - Validate license for a system
- `POST /licenses/verify` - Verify license token (sets organization as verified)
- `POST /licenses/check_expiration` - Check license expiration status
- `POST /licenses/renew` - Renew expired license

### Organization Management
- `POST /organizations/` - Create organization (auto-seeds data)
- `GET /organizations/` - List organizations
- `GET /organizations/{id}` - Get organization details
- `PUT /organizations/{id}` - Update organization
- `DELETE /organizations/{id}` - Delete organization

### Other Endpoints
- Authentication, Users, Outlets, Products, Sales, Purchases, etc.

## Integration with Tauri

The executable can be bundled with your Tauri application. The backend will run on `http://localhost:8000` by default.

### Example Tauri Configuration
```json
{
  "scripts": {
    "dev": "npm run tauri dev",
    "build": "npm run tauri build"
  },
  "tauri": {
    "bundle": {
      "externalBin": [
        "../inventory_api/dist/inventory_backend.exe"
      ]
    }
  }
}
```

## Database
The application uses SQLite by default (`inventory.db`). For production, configure PostgreSQL in `app/database.py`.

## License Verification Flow
1. License is generated on Supabase website
2. Client receives license token via email
3. Client calls `/licenses/verify` with license_key
4. Organization status is set to 'verified'
5. Subsequent validations check expiration and active status

## Troubleshooting

### Common Issues
- **Port already in use**: Change port in `app/main.py` or kill process on port 8000
- **Database connection failed**: Check Supabase credentials in environment variables
- **Executable won't start**: Ensure all dependencies are installed before building

### Logs
Check console output for detailed error messages and logs.
