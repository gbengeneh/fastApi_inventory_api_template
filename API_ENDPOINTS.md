# Inventory POS System API Endpoints

## Authentication Endpoints (`/api/auth`)
- `POST /api/auth/token` - Login for access token
- `POST /api/auth/register` - Register new user
- `GET /api/auth/me` - Get current user info

## User Management (`/api`)
- `GET /api/users/` - List users (authenticated)
- `GET /api/users/{user_id}` - Get specific user (authenticated)
- `POST /api/users/` - Create user (admin only)
- `PUT /api/users/{user_id}` - Update user (admin only)
- `DELETE /api/users/{user_id}` - Delete user (admin only)
- `GET /api/activity-logs/` - List activity logs (authenticated)
- `POST /api/activity-logs/` - Create activity log (authenticated)

## Outlets (`/api`)
- `GET /api/outlets/` - List outlets
- `GET /api/outlets/{outlet_id}` - Get specific outlet
- `POST /api/outlets/` - Create outlet
- `PUT /api/outlets/{outlet_id}` - Update outlet
- `DELETE /api/outlets/{outlet_id}` - Delete outlet
- `GET /api/cashier-stations/` - List cashier stations
- `GET /api/cashier-stations/{station_id}` - Get specific cashier station
- `POST /api/cashier-stations/` - Create cashier station
- `PUT /api/cashier-stations/{station_id}` - Update cashier station
- `DELETE /api/cashier-stations/{station_id}` - Delete cashier station

## Products (`/api`)
- `GET /api/categories/` - List categories
- `GET /api/categories/{category_id}` - Get specific category
- `POST /api/categories/` - Create category (admin only)
- `PUT /api/categories/{category_id}` - Update category (admin only)
- `DELETE /api/categories/{category_id}` - Delete category (admin only)
- `GET /api/units/` - List units
- `GET /api/units/{unit_id}` - Get specific unit
- `POST /api/units/` - Create unit (admin only)
- `PUT /api/units/{unit_id}` - Update unit (admin only)
- `DELETE /api/units/{unit_id}` - Delete unit (admin only)
- `GET /api/products/` - List products
- `GET /api/products/{product_id}` - Get specific product
- `POST /api/products/` - Create product (admin only)
- `POST /api/products/bulk/` - Bulk create products (admin only, accepts array of products, tax_rate in decimal 0-1, optional)
- `PUT /api/products/{product_id}` - Update product (admin only)
- `DELETE /api/products/{product_id}` - Delete product (admin only)

## Suppliers & Purchases (`/api`)
- `GET /api/suppliers/` - List suppliers
- `GET /api/suppliers/{supplier_id}` - Get specific supplier
- `POST /api/suppliers/` - Create supplier
- `PUT /api/suppliers/{supplier_id}` - Update supplier
- `DELETE /api/suppliers/{supplier_id}` - Delete supplier
- `GET /api/purchases/` - List purchases
- `GET /api/purchases/{purchase_id}` - Get specific purchase
- `POST /api/purchases/` - Create purchase (authenticated, updates product stock & cost)
- `PUT /api/purchases/{purchase_id}` - Update purchase
- `DELETE /api/purchases/{purchase_id}` - Delete purchase
- `GET /api/purchase-items/` - List purchase items
- `GET /api/purchase-items/{item_id}` - Get specific purchase item
- `POST /api/purchase-items/` - Create purchase item
- `PUT /api/purchase-items/{item_id}` - Update purchase item
- `DELETE /api/purchase-items/{item_id}` - Delete purchase item

## Sales (`/api`)
- `GET /api/sales/` - List sales
- `GET /api/sales/{sale_id}` - Get specific sale
- `POST /api/sales/` - Create sale
- `PUT /api/sales/{sale_id}` - Update sale
- `DELETE /api/sales/{sale_id}` - Delete sale
- `GET /api/sales/{sale_id}/invoice` - Generate customized invoice for sale (uses outlet's default printer settings and invoice template)
- `POST /api/sales/{sale_id}/print` - Print invoice for sale (falls back to PDF if no printer configured)
- `POST /api/sales/{sale_id}/payments/` - Create sale payment (links payment to sale)
- `GET /api/sales/{sale_id}/payments/` - List payments for a specific sale
- `DELETE /api/sales/{sale_id}/payments/{payment_id}` - Delete sale payment
- `GET /api/sale-items/` - List sale items
- `GET /api/sale-items/{item_id}` - Get specific sale item
- `POST /api/sale-items/` - Create sale item
- `PUT /api/sale-items/{item_id}` - Update sale item
- `DELETE /api/sale-items/{item_id}` - Delete sale item
- `GET /api/payments/` - List payments
- `GET /api/payments/{payment_id}` - Get specific payment
- `POST /api/payments/` - Create payment
- `PUT /api/payments/{payment_id}` - Update payment
- `DELETE /api/payments/{payment_id}` - Delete payment

## Cashier Shifts (`/api`)
- `GET /api/cashier-shifts/` - List cashier shifts
- `GET /api/cashier-shifts/{shift_id}` - Get specific cashier shift
- `POST /api/cashier-shifts/` - Create cashier shift (starts shift with opening balance)
- `PUT /api/cashier-shifts/{shift_id}` - Update cashier shift (closes shift with closing balance)
- `DELETE /api/cashier-shifts/{shift_id}` - Delete cashier shift

## Settings (`/api`)
- `GET /api/printer-settings/` - List printer settings
- `GET /api/printer-settings/{setting_id}` - Get specific printer setting
- `POST /api/printer-settings/` - Create printer setting
- `PUT /api/printer-settings/{setting_id}` - Update printer setting
- `DELETE /api/printer-settings/{setting_id}` - Delete printer setting
- `GET /api/invoice-templates/` - List invoice templates
- `GET /api/invoice-templates/{template_id}` - Get specific invoice template
- `POST /api/invoice-templates/` - Create invoice template
- `PUT /api/invoice-templates/{template_id}` - Update invoice template
- `DELETE /api/invoice-templates/{template_id}` - Delete invoice template
- `GET /api/outlets/{outlet_id}/default-printer` - Get default printer for outlet
- `GET /api/outlets/{outlet_id}/default-template` - Get default invoice template for outlet
- `GET /api/printers/installed` - Get list of installed printers on the system

## Root Endpoint
- `GET /` - Root endpoint (no auth required)
