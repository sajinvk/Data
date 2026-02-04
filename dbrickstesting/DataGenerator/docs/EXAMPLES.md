# Example Configuration Templates for AI Data Generator

This file contains ready-to-use configuration templates for common use cases.
Copy and paste these into the configuration section of `ai_data_generator.py`.

## Healthcare Examples

### Example 1: Patient Records
```python
INDUSTRY = "healthcare"
DOMAIN = "patient records"
TABLE_NAME = "patients"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 100
CUSTOM_SCHEMA = None  # Let AI generate
COLUMN_CONSTRAINTS = {
    "patient_id": "Unique integers starting from 10000",
    "age": "Ages between 0 and 100",
    "diagnosis": "Common medical conditions"
}
```

### Example 2: Medical Appointments
```python
INDUSTRY = "healthcare"
DOMAIN = "medical appointment scheduling"
TABLE_NAME = "appointments"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 200
CUSTOM_SCHEMA = {
    "appointment_id": "INT",
    "patient_id": "INT",
    "doctor_name": "STRING",
    "appointment_date": "TIMESTAMP",
    "appointment_type": "STRING",
    "duration_minutes": "INT",
    "status": "STRING",
    "notes": "STRING"
}
COLUMN_CONSTRAINTS = {
    "appointment_id": "Sequential IDs starting from 1",
    "patient_id": "Between 10000 and 20000",
    "duration_minutes": "15, 30, 45, or 60 minutes",
    "status": "scheduled, completed, cancelled, or no-show"
}
```

### Example 3: Prescription Records
```python
INDUSTRY = "healthcare"
DOMAIN = "prescription records"
TABLE_NAME = "prescriptions"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 150
CUSTOM_SCHEMA = None  # Let AI generate
COLUMN_CONSTRAINTS = {
    "prescription_id": "Sequential starting from 1",
    "medication_name": "Common prescription medications",
    "dosage": "Realistic dosages with units (mg, ml, etc)",
    "refills_remaining": "Between 0 and 5"
}
```

## Retail Examples

### Example 4: Product Catalog
```python
INDUSTRY = "retail"
DOMAIN = "product inventory"
TABLE_NAME = "products"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 100
CUSTOM_SCHEMA = {
    "product_id": "INT",
    "product_name": "STRING",
    "category": "STRING",
    "subcategory": "STRING",
    "price": "DOUBLE",
    "cost": "DOUBLE",
    "stock_quantity": "INT",
    "supplier": "STRING",
    "last_restocked": "DATE",
    "is_active": "BOOLEAN"
}
COLUMN_CONSTRAINTS = {
    "product_id": "Range between 1 and 100",
    "price": "Between 5.00 and 500.00",
    "cost": "Between 2.00 and 300.00 (less than price)",
    "stock_quantity": "Between 0 and 1000",
    "category": "Electronics, Clothing, Home & Garden, Sports, or Toys"
}
```

### Example 5: Customer Orders
```python
INDUSTRY = "retail"
DOMAIN = "customer order transactions"
TABLE_NAME = "orders"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 300
CUSTOM_SCHEMA = None  # Let AI generate
COLUMN_CONSTRAINTS = {
    "order_id": "Unique sequential integers",
    "customer_id": "Between 1 and 100",
    "order_total": "Between 10.00 and 1000.00",
    "order_status": "pending, processing, shipped, delivered, or cancelled",
    "payment_method": "credit_card, debit_card, paypal, or cash"
}
```

### Example 6: Store Locations
```python
INDUSTRY = "retail"
DOMAIN = "store location data"
TABLE_NAME = "stores"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 50
CUSTOM_SCHEMA = {
    "store_id": "INT",
    "store_name": "STRING",
    "address": "STRING",
    "city": "STRING",
    "state": "STRING",
    "country": "STRING",
    "postal_code": "STRING",
    "phone": "STRING",
    "opening_date": "DATE",
    "square_footage": "INT",
    "employee_count": "INT"
}
COLUMN_CONSTRAINTS = {
    "store_id": "Sequential from 1",
    "country": "Australia, United States, United Kingdom, or Canada",
    "square_footage": "Between 5000 and 50000",
    "employee_count": "Between 10 and 200"
}
```

## Finance Examples

### Example 7: Transaction Records
```python
INDUSTRY = "finance"
DOMAIN = "transaction records"
TABLE_NAME = "transactions"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 500
CUSTOM_SCHEMA = {
    "transaction_id": "BIGINT",
    "account_number": "STRING",
    "transaction_date": "TIMESTAMP",
    "amount": "DOUBLE",
    "transaction_type": "STRING",
    "merchant": "STRING",
    "category": "STRING",
    "status": "STRING",
    "card_type": "STRING",
    "is_fraud": "BOOLEAN"
}
COLUMN_CONSTRAINTS = {
    "transaction_id": "Unique sequential IDs starting from 100000",
    "amount": "Between 10.00 and 10000.00",
    "transaction_type": "debit or credit",
    "status": "completed, pending, or failed",
    "is_fraud": "Mostly false, occasionally true (5%)",
    "category": "groceries, dining, entertainment, utilities, shopping, travel, or healthcare"
}
```

### Example 8: Loan Applications
```python
INDUSTRY = "finance"
DOMAIN = "loan application processing"
TABLE_NAME = "loan_applications"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 150
CUSTOM_SCHEMA = None  # Let AI generate
COLUMN_CONSTRAINTS = {
    "application_id": "Sequential from 1",
    "loan_amount": "Between 5000 and 500000",
    "loan_type": "personal, mortgage, auto, or business",
    "credit_score": "Between 300 and 850",
    "annual_income": "Between 20000 and 500000",
    "employment_status": "employed, self-employed, unemployed, or retired",
    "application_status": "pending, approved, denied, or under_review"
}
```

### Example 9: Investment Portfolio
```python
INDUSTRY = "finance"
DOMAIN = "investment portfolio holdings"
TABLE_NAME = "portfolio_holdings"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 200
CUSTOM_SCHEMA = {
    "holding_id": "INT",
    "account_id": "INT",
    "ticker_symbol": "STRING",
    "asset_type": "STRING",
    "shares": "DOUBLE",
    "purchase_price": "DOUBLE",
    "current_price": "DOUBLE",
    "purchase_date": "DATE",
    "last_updated": "TIMESTAMP"
}
COLUMN_CONSTRAINTS = {
    "ticker_symbol": "Realistic stock ticker symbols (3-5 letters)",
    "asset_type": "stock, bond, ETF, mutual_fund, or cryptocurrency",
    "shares": "Between 1 and 10000",
    "purchase_price": "Between 10.00 and 5000.00",
    "current_price": "Between 10.00 and 5000.00"
}
```

## Insurance Examples

### Example 10: Insurance Claims
```python
INDUSTRY = "insurance"
DOMAIN = "claims processing"
TABLE_NAME = "claims"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 200
CUSTOM_SCHEMA = {
    "claim_id": "INT",
    "policy_number": "STRING",
    "claim_date": "TIMESTAMP",
    "claim_type": "STRING",
    "claim_amount": "DOUBLE",
    "claim_status": "STRING",
    "adjuster_name": "STRING",
    "description": "STRING",
    "approved_amount": "DOUBLE",
    "settlement_date": "DATE"
}
COLUMN_CONSTRAINTS = {
    "claim_id": "Unique integers starting from 5000",
    "claim_amount": "Between 100.00 and 50000.00",
    "claim_status": "pending, approved, denied, or investigating",
    "claim_type": "medical, dental, accident, property, or liability",
    "approved_amount": "Between 0 and claim_amount (sometimes 0 if denied)"
}
```

### Example 11: Policy Records
```python
INDUSTRY = "insurance"
DOMAIN = "policy management"
TABLE_NAME = "policies"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 150
CUSTOM_SCHEMA = None  # Let AI generate
COLUMN_CONSTRAINTS = {
    "policy_number": "Format like POL-12345",
    "policy_type": "health, auto, home, life, or travel",
    "premium_amount": "Between 50.00 and 5000.00",
    "coverage_amount": "Between 10000 and 1000000",
    "status": "active, expired, cancelled, or lapsed"
}
```

## Manufacturing Examples

### Example 12: Equipment Maintenance
```python
INDUSTRY = "manufacturing"
DOMAIN = "equipment maintenance records"
TABLE_NAME = "maintenance_logs"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 250
CUSTOM_SCHEMA = {
    "maintenance_id": "INT",
    "equipment_id": "STRING",
    "equipment_name": "STRING",
    "maintenance_date": "TIMESTAMP",
    "maintenance_type": "STRING",
    "technician": "STRING",
    "cost": "DOUBLE",
    "downtime_hours": "INT",
    "parts_replaced": "STRING",
    "is_critical": "BOOLEAN"
}
COLUMN_CONSTRAINTS = {
    "equipment_id": "Format like EQ-1001, EQ-1002",
    "cost": "Between 50.00 and 5000.00",
    "downtime_hours": "Between 0 and 48",
    "maintenance_type": "preventive, corrective, predictive, or emergency"
}
```

### Example 13: Production Batches
```python
INDUSTRY = "manufacturing"
DOMAIN = "production batch tracking"
TABLE_NAME = "production_batches"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 100
CUSTOM_SCHEMA = None  # Let AI generate
COLUMN_CONSTRAINTS = {
    "batch_id": "Format like BATCH-2024-001",
    "quantity_produced": "Between 100 and 10000",
    "defect_rate": "Between 0.0 and 5.0 percent",
    "quality_score": "Between 70 and 100",
    "status": "in_progress, completed, quality_check, or rejected"
}
```

## Logistics Examples

### Example 14: Shipment Tracking
```python
INDUSTRY = "logistics"
DOMAIN = "shipment tracking"
TABLE_NAME = "shipments"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 200
CUSTOM_SCHEMA = {
    "shipment_id": "STRING",
    "order_id": "INT",
    "origin_city": "STRING",
    "destination_city": "STRING",
    "carrier": "STRING",
    "ship_date": "TIMESTAMP",
    "estimated_delivery": "TIMESTAMP",
    "actual_delivery": "TIMESTAMP",
    "weight_kg": "DOUBLE",
    "status": "STRING",
    "tracking_number": "STRING"
}
COLUMN_CONSTRAINTS = {
    "shipment_id": "Format like SHP-12345",
    "carrier": "FedEx, UPS, DHL, USPS, or Australia Post",
    "weight_kg": "Between 0.5 and 1000",
    "status": "pending, in_transit, out_for_delivery, delivered, or delayed"
}
```

### Example 15: Warehouse Inventory
```python
INDUSTRY = "logistics"
DOMAIN = "warehouse inventory management"
TABLE_NAME = "warehouse_inventory"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 300
CUSTOM_SCHEMA = None  # Let AI generate
COLUMN_CONSTRAINTS = {
    "sku": "Format like SKU-A1234",
    "warehouse_location": "Format like AISLE-A-SHELF-12",
    "quantity_on_hand": "Between 0 and 5000",
    "reorder_point": "Between 10 and 500",
    "last_inventory_date": "Recent dates within last 90 days"
}
```

## Education Examples

### Example 16: Student Records
```python
INDUSTRY = "education"
DOMAIN = "student enrollment records"
TABLE_NAME = "students"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 150
CUSTOM_SCHEMA = {
    "student_id": "INT",
    "first_name": "STRING",
    "last_name": "STRING",
    "date_of_birth": "DATE",
    "enrollment_date": "DATE",
    "grade_level": "STRING",
    "gpa": "DOUBLE",
    "major": "STRING",
    "email": "STRING",
    "is_active": "BOOLEAN"
}
COLUMN_CONSTRAINTS = {
    "student_id": "Sequential starting from 1000",
    "grade_level": "Freshman, Sophomore, Junior, or Senior",
    "gpa": "Between 0.0 and 4.0",
    "major": "Common college majors"
}
```

### Example 17: Course Registrations
```python
INDUSTRY = "education"
DOMAIN = "course registration system"
TABLE_NAME = "course_registrations"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 400
CUSTOM_SCHEMA = None  # Let AI generate
COLUMN_CONSTRAINTS = {
    "registration_id": "Sequential from 1",
    "student_id": "Between 1000 and 2000",
    "course_code": "Format like CS101, MATH201, ENG150",
    "semester": "Fall 2024, Spring 2025, or Summer 2025",
    "grade": "A, A-, B+, B, B-, C+, C, or null if in progress"
}
```

## Hospitality Examples

### Example 18: Hotel Reservations
```python
INDUSTRY = "hospitality"
DOMAIN = "hotel reservation system"
TABLE_NAME = "reservations"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 200
CUSTOM_SCHEMA = {
    "reservation_id": "STRING",
    "guest_name": "STRING",
    "email": "STRING",
    "phone": "STRING",
    "check_in_date": "DATE",
    "check_out_date": "DATE",
    "room_type": "STRING",
    "number_of_guests": "INT",
    "total_cost": "DOUBLE",
    "status": "STRING",
    "special_requests": "STRING"
}
COLUMN_CONSTRAINTS = {
    "reservation_id": "Format like RES-2024-12345",
    "room_type": "standard, deluxe, suite, or penthouse",
    "number_of_guests": "Between 1 and 6",
    "total_cost": "Between 100.00 and 2000.00",
    "status": "confirmed, checked_in, checked_out, or cancelled"
}
```

## Telecommunications Examples

### Example 19: Customer Service Tickets
```python
INDUSTRY = "telecommunications"
DOMAIN = "customer service ticket management"
TABLE_NAME = "support_tickets"
TARGET_CATALOG = "pilotws"
TARGET_SCHEMA = "pilotschema"
NUM_ROWS = 300
CUSTOM_SCHEMA = {
    "ticket_id": "STRING",
    "customer_id": "INT",
    "issue_type": "STRING",
    "priority": "STRING",
    "status": "STRING",
    "created_date": "TIMESTAMP",
    "resolved_date": "TIMESTAMP",
    "assigned_agent": "STRING",
    "resolution_time_hours": "INT",
    "satisfaction_score": "INT"
}
COLUMN_CONSTRAINTS = {
    "ticket_id": "Format like TKT-12345",
    "issue_type": "billing, technical, service_outage, or general_inquiry",
    "priority": "low, medium, high, or critical",
    "status": "open, in_progress, resolved, or closed",
    "resolution_time_hours": "Between 1 and 72",
    "satisfaction_score": "Between 1 and 5"
}
```

## Tips for Using These Templates

1. **Modify as needed**: These are starting points - adjust to your specific needs
2. **Test with small datasets**: Start with 50-100 rows to validate
3. **Iterate on constraints**: Refine constraints based on initial results
4. **Combine templates**: Use multiple templates to create related tables
5. **Adjust NUM_ROWS**: Scale up once you're satisfied with the data quality
