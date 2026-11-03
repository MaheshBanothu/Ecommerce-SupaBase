# E-Commerce-CodeGnan
# Local MySQL to Supabase PostgreSQL Migration Guide

## 1. Overview

This document explains how the Flask E-Commerce application was migrated from a locally hosted MySQL database to **Supabase PostgreSQL**.

The existing Flask application was updated to communicate with Supabase PostgreSQL using the `psycopg2` Python driver.

The application logic and existing features are retained while database connections, SQL queries, data types, and database operations were adapted for PostgreSQL compatibility.

### Migration Summary

| Component | Before Migration | After Migration |
|---|---|---|
| Database | Local MySQL | Supabase PostgreSQL |
| Database hosting | Local machine | Supabase Cloud |
| Python database driver | MySQL connector | psycopg2 |
| Database connection | Local database connection | Remote PostgreSQL connection |
| Database credentials | Local configuration | Environment variables in `.env` |
| Database schema | MySQL tables | PostgreSQL tables |
| Auto-increment columns | AUTO_INCREMENT | GENERATED AS IDENTITY |
| Enum columns | MySQL ENUM | PostgreSQL ENUM types |
| Generated columns | MySQL generated columns | PostgreSQL generated stored columns |
| Updated timestamps | ON UPDATE CURRENT_TIMESTAMP | PostgreSQL triggers |
| SSL | Not required locally | Required for the configured connection |

### Important Migration Notes

- The original local MySQL database remains untouched.
- Existing MySQL records are not automatically transferred.
- The Supabase database starts with an empty dataset.
- Database tables are managed directly through Supabase.
- Flask does not automatically create database tables.
- The application connects directly to PostgreSQL using `psycopg2`.
- The application uses its own user authentication logic.
- Supabase Authentication is not automatically connected to the application's `users` table.
- Row Level Security (RLS) is disabled in the current project configuration.
- Product images continue to be stored in the application's local static directory.

---

# 2. Files Modified

The following files were modified to support Supabase PostgreSQL.

| File | Changes |
|---|---|
| `app.py` | Updated database-related application logic, environment variable loading, category operations and PostgreSQL-compatible queries. |
| `database/connection.py` | Replaced the MySQL connection implementation with a PostgreSQL connection using `psycopg2`. |
| `database/tables.py` | Removed automatic table creation. The database schema is now managed directly through Supabase. |
| `database/utilsDB.py` | Updated authentication and user-related database queries for PostgreSQL. |
| `database/userDB.py` | Updated cart, order and payment database operations for PostgreSQL. |
| `database/adminDB.py` | Updated admin operations and SQL queries for PostgreSQL compatibility. |
| `database/__init__.py` | Updated database module imports. |
| `.env` | Added environment-based PostgreSQL connection configuration. |
| `.gitignore` | Added the virtual environment directory to Git exclusions. |

### Important Implementation Changes

#### Database Connection

- Replaced MySQL connection logic with `psycopg2`.
- Added SSL support using `sslmode=require`.
- Added environment variable validation.
- Added compatibility for existing code using `cursor(dictionary=True)`.
- Added connection status checking.
- Used `RealDictCursor` for dictionary-style database results.

#### SQL Compatibility

- Replaced MySQL-specific SQL syntax with PostgreSQL-compatible syntax.
- Updated enum comparisons and assignments using PostgreSQL casts.
- Used PostgreSQL `RETURNING` to retrieve generated IDs.
- Updated transaction handling with commit and rollback.
- Updated generated columns and timestamp handling.
- Updated database queries to work with PostgreSQL data types.

#### Database Schema Management

- Removed automatic table creation from application startup.
- Database tables are created and managed through Supabase SQL Editor.
- PostgreSQL enum types, constraints, indexes and triggers are managed through Supabase.

---

# 3. Supabase Database Setup

Follow these steps to create your own Supabase PostgreSQL database.

## Step 1: Create a Supabase Account

1. Open https://supabase.com/
2. Click **Start your project**.
3. Sign up using GitHub or your email address.
4. Complete email verification if requested.
5. Log in to the Supabase Dashboard.

Dashboard:

https://supabase.com/dashboard

## Step 2: Create a Supabase Organization

If you do not already have an organization:

1. Open the Supabase Dashboard.
2. Click **New organization**.
3. Enter an organization name.
4. Select the appropriate plan.
5. Complete organization creation.

If you already have an organization, select it and continue.

## Step 3: Create a New Supabase Project

1. Open the Supabase Dashboard.
2. Select your organization.
3. Click **New project**.
4. Enter the following details:

| Field | Value |
|---|---|
| Project name | E-Commerce-Supabase |
| Database password | Create a strong password |
| Region | Select a region close to your application users |
| Pricing plan | Select the appropriate plan |

5. Save your database password securely.
6. Click **Create new project**.
7. Wait until Supabase finishes provisioning the project.

**Important:** The database password is different from your Supabase account password.

It is the password used to connect to the PostgreSQL database.

Do not lose it.

---

# 4. Create the PostgreSQL Database Schema

The application requires seven PostgreSQL tables and five PostgreSQL enum types.

## Step 1: Open the SQL Editor

After creating your Supabase project:

1. Open your project.
2. Locate **SQL Editor** in the left sidebar.
3. Click **SQL Editor**.
4. Click **New query**.
5. Give the query a name such as `Ecommerce Database Schema`.

You will execute the complete database creation script from this screen.

## Step 2: Understand the Required Tables

| Table | Purpose |
|---|---|
| `users` | Stores user accounts and authentication information. |
| `products` | Stores product information. |
| `categories` | Stores product categories. |
| `orders` | Stores customer orders. |
| `order_details` | Stores individual products belonging to orders. |
| `payments` | Stores payment information. |
| `cart` | Stores customer cart items. |

## Step 3: Understand the PostgreSQL Enum Types

| Enum Type | Allowed Values |
|---|---|
| `user_role` | `admin`, `user` |
| `user_gender` | `male`, `female` |
| `order_status` | `shipped`, `delivered`, `cancelled`, `pending` |
| `payment_method` | `cash`, `upi`, `netbanking` |
| `payment_status` | `pending`, `success`, `failed` |

## Step 4: Execute the Complete PostgreSQL Schema

**Important:**

- Execute this script only on a new, empty Supabase database.
- Do not execute it on an existing database that already contains these tables and enum types.
- The script creates database structures only.
- It does not import existing MySQL records.
- Do not execute the original MySQL schema directly in PostgreSQL.

Copy the complete SQL script below.

Open:

**Supabase Dashboard → SQL Editor → New query**

Paste the script and click **Run**.

### Complete PostgreSQL Schema

```sql
-- =========================================================
-- 1. CREATE ENUM TYPES
-- =========================================================

CREATE TYPE public.user_role AS ENUM (
    'admin',
    'user'
);

CREATE TYPE public.user_gender AS ENUM (
    'male',
    'female'
);

CREATE TYPE public.order_status AS ENUM (
    'shipped',
    'delivered',
    'cancelled',
    'pending'
);

CREATE TYPE public.payment_method AS ENUM (
    'cash',
    'upi',
    'netbanking'
);

CREATE TYPE public.payment_status AS ENUM (
    'pending',
    'success',
    'failed'
);


-- =========================================================
-- 2. CREATE USERS TABLE
-- =========================================================

CREATE TABLE public.users (
    userid BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,

    username VARCHAR(50) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    hashpassword VARCHAR(255) NOT NULL,

    role public.user_role NOT NULL DEFAULT 'user',
    gender public.user_gender,

    phone VARCHAR(20),
    dateofbirth DATE,

    profilename VARCHAR(255),
    profilepath VARCHAR(255),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 3. CREATE CATEGORIES TABLE
-- =========================================================

CREATE TABLE public.categories (
    categoryid INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,

    categoryname VARCHAR(120) NOT NULL UNIQUE,
    description TEXT
);


-- =========================================================
-- 4. CREATE PRODUCTS TABLE
-- =========================================================

CREATE TABLE public.products (
    productid BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,

    productname VARCHAR(100) NOT NULL,
    description TEXT,

    category VARCHAR(50),

    quantity INTEGER NOT NULL DEFAULT 0,

    buyprice NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    saleprice NUMERIC(12,2) NOT NULL DEFAULT 0.00,

    imgname VARCHAR(255),
    storedpath VARCHAR(500),

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 5. CREATE ORDERS TABLE
-- =========================================================

CREATE TABLE public.orders (
    orderid BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,

    userid BIGINT NOT NULL,

    status public.order_status NOT NULL DEFAULT 'pending',

    address VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_orders_user
        FOREIGN KEY (userid)
        REFERENCES public.users(userid)
);


-- =========================================================
-- 6. CREATE ORDER_DETAILS TABLE
-- =========================================================

CREATE TABLE public.order_details (
    orderid BIGINT NOT NULL,
    productid BIGINT NOT NULL,

    quantity INTEGER NOT NULL DEFAULT 1,

    price NUMERIC(12,2) NOT NULL DEFAULT 0.00,

    subtotal NUMERIC(14,2)
        GENERATED ALWAYS AS (quantity * price) STORED,

    PRIMARY KEY (orderid, productid),

    CONSTRAINT fk_order_details_order
        FOREIGN KEY (orderid)
        REFERENCES public.orders(orderid),

    CONSTRAINT fk_order_details_product
        FOREIGN KEY (productid)
        REFERENCES public.products(productid)
);


-- =========================================================
-- 7. CREATE PAYMENTS TABLE
-- =========================================================

CREATE TABLE public.payments (
    paymentid BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,

    userid BIGINT NOT NULL,
    orderid BIGINT NOT NULL,

    method public.payment_method,

    amount NUMERIC(14,2) NOT NULL DEFAULT 0.00,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    status public.payment_status DEFAULT 'pending',

    razorpay_order_id VARCHAR(100),
    razorpay_payment_id VARCHAR(100),

    CONSTRAINT fk_payments_user
        FOREIGN KEY (userid)
        REFERENCES public.users(userid),

    CONSTRAINT fk_payments_order
        FOREIGN KEY (orderid)
        REFERENCES public.orders(orderid)
);


-- =========================================================
-- 8. CREATE CART TABLE
-- =========================================================

CREATE TABLE public.cart (
    cartid BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,

    userid BIGINT NOT NULL,
    productid BIGINT NOT NULL,

    quantity INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT uq_cart_user_product
        UNIQUE (userid, productid),

    CONSTRAINT fk_cart_user
        FOREIGN KEY (userid)
        REFERENCES public.users(userid),

    CONSTRAINT fk_cart_product
        FOREIGN KEY (productid)
        REFERENCES public.products(productid)
);


-- =========================================================
-- 9. CREATE FOREIGN KEY INDEXES
-- =========================================================

CREATE INDEX idx_orders_user
ON public.orders(userid);

CREATE INDEX idx_order_details_product
ON public.order_details(productid);

CREATE INDEX idx_payments_user
ON public.payments(userid);

CREATE INDEX idx_payments_order
ON public.payments(orderid);

CREATE INDEX idx_cart_product
ON public.cart(productid);


-- =========================================================
-- 10. CREATE UPDATED_AT TRIGGER FUNCTION
-- =========================================================

CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


-- =========================================================
-- 11. CREATE USERS UPDATED_AT TRIGGER
-- =========================================================

CREATE TRIGGER users_updated_at
BEFORE UPDATE ON public.users
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at();


-- =========================================================
-- 12. CREATE PRODUCTS UPDATED_AT TRIGGER
-- =========================================================

CREATE TRIGGER products_updated_at
BEFORE UPDATE ON public.products
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at();


-- =========================================================
-- DATABASE SCHEMA CREATION COMPLETED
-- =========================================================
```

## Step 5: Understand the MySQL to PostgreSQL Changes

The original MySQL schema was adapted using the following PostgreSQL equivalents.

| MySQL | PostgreSQL |
|---|---|
| `AUTO_INCREMENT` | `GENERATED BY DEFAULT AS IDENTITY` |
| MySQL `ENUM` | PostgreSQL enum type |
| `TINYINT(1)` | `BOOLEAN` |
| `DECIMAL` | `NUMERIC` |
| Generated columns | Generated stored columns |
| `ON UPDATE CURRENT_TIMESTAMP` | PostgreSQL trigger |
| MySQL SQL syntax | PostgreSQL-compatible SQL syntax |

The following database relationships are maintained:

- `orders.userid` references `users.userid`.
- `order_details.orderid` references `orders.orderid`.
- `order_details.productid` references `products.productid`.
- `payments.userid` references `users.userid`.
- `payments.orderid` references `orders.orderid`.
- `cart.userid` references `users.userid`.
- `cart.productid` references `products.productid`.

The `cart` table also has a unique constraint on `(userid, productid)`.

The `order_details` table uses a composite primary key on `(orderid, productid)`.

The `subtotal` column is generated automatically using:

```sql
quantity * price
```

The `users` and `products` tables use triggers to update their `updated_at` values whenever a record is modified.

**Category relationship:** The `products.category` column stores the category name as text. It is not a foreign key to `categories.categoryname`. The application separately maintains the category master table.

---

# 5. Verify Database Creation

After executing the SQL script successfully, verify that all database objects were created.

## Step 1: Verify Tables Through Table Editor

1. Open the Supabase Dashboard.
2. Select your project.
3. Click **Table Editor** in the left sidebar.
4. Make sure the selected schema is `public`.

You should see the following seven tables:

- `users`
- `products`
- `categories`
- `orders`
- `order_details`
- `payments`
- `cart`

Open each table and verify its columns.

## Step 2: Verify All Seven Tables Using SQL

Open:

**SQL Editor → New query**

Execute:

```sql
SELECT
    table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;
```

Expected tables:

```text
cart
categories
order_details
orders
payments
products
users
```

## Step 3: Verify PostgreSQL Enum Types

Execute:

```sql
SELECT
    t.typname AS enum_name,
    e.enumlabel AS enum_value
FROM pg_type t
JOIN pg_enum e
    ON t.oid = e.enumtypid
JOIN pg_namespace n
    ON n.oid = t.typnamespace
WHERE n.nspname = 'public'
ORDER BY t.typname, e.enumsortorder;
```

Verify the five enum types and their allowed values.

## Step 4: Verify Table Columns

Execute:

```sql
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
```

This displays the columns, data types, nullability and default values of all application tables.

## Step 5: Verify Foreign Keys

Execute:

```sql
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.constraint_schema = kcu.constraint_schema
JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.constraint_schema = tc.constraint_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_schema = 'public'
ORDER BY tc.table_name;
```

Verify that all expected relationships are present.

## Step 6: Verify Triggers

Execute:

```sql
SELECT
    trigger_name,
    event_object_table,
    action_timing,
    event_manipulation
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table;
```

Expected triggers:

- `users_updated_at`
- `products_updated_at`

---

# 6. Configure Supabase Database Connection

The Flask application connects directly to Supabase PostgreSQL using `psycopg2`.

It does not use the Supabase REST API for its database operations.

## Step 1: Open Supabase Connection Settings

1. Open your Supabase project.
2. Click the **Connect** button near the project header.
3. Locate the connection string section.
4. Select the PostgreSQL connection URI.
5. Copy the connection string.

Alternatively:

1. Open **Project Settings**.
2. Navigate to **Database**.
3. Locate the database connection information.

Supabase provides different connection options, including direct and pooled connections.

Use a connection option compatible with `psycopg2`.

If direct connectivity is unavailable on your network, use the appropriate Supabase session pooler connection details.

## Step 2: Understand the Connection String

A typical PostgreSQL connection URI looks like:

```text
postgresql://postgres:YOUR_PASSWORD@YOUR_HOST:5432/postgres
```

| Component | Description |
|---|---|
| `postgresql://` | PostgreSQL protocol |
| `postgres` | Database username |
| `YOUR_PASSWORD` | Database password |
| `YOUR_HOST` | Supabase database hostname |
| `5432` | PostgreSQL direct connection port |
| `postgres` | Database name |

Use the exact connection information provided by Supabase.

Do not assume that every connection option uses the same username or port.

## Step 3: Configure the `.env` File

Open your project root directory.

Locate the `.env` file.

If it does not exist, create one.

Add the following configuration:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_HOST:5432/postgres
DB_SSLMODE=require
```

Replace the placeholders with your own Supabase connection details.

### Password Encoding

If your database password contains special characters such as:

- `@`
- `#`
- `%`
- `/`
- `:`

URL-encode the password before placing it inside the connection URI.

### Important Security Instructions

- Never hardcode database credentials in Python files.
- Never expose the database password in frontend code.
- Keep your actual `.env` credentials private.
- The `.env` file committed in this repository contains placeholders only.
- Do not use your database password as a Supabase API key.

---

# 7. Supabase API Keys and Database Credentials

This project uses a direct PostgreSQL connection.

Therefore, the Flask application's database connection requires:

- PostgreSQL connection URI.
- Database username.
- Database password.
- Database hostname.
- Database port.
- Database name.
- SSL configuration.

### Are Supabase API Keys Required?

The current application does not use Supabase REST API calls for its database operations.

Therefore, the following API keys are not required for the current direct PostgreSQL connection:

- Supabase publishable key / legacy `anon` key.
- Supabase secret key / legacy `service_role` key.

Do not place privileged Supabase keys in frontend code.

If Supabase API services are introduced later, configure the relevant keys separately and securely.

---

# 8. Install Python Dependencies

## Step 1: Open the Project Directory

Open PowerShell or the VS Code terminal.

Navigate to the project:

```powershell
cd E-Commerce-Supabase
```

## Step 2: Create a Virtual Environment

```powershell
python -m venv venv
```

## Step 3: Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

After activation, the terminal should show the virtual environment name.

For example:

```text
(venv) PS C:\...\E-Commerce-Supabase>
```

## Step 4: Install Dependencies

If the repository contains `requirements.txt`, execute:

```powershell
python -m pip install -r requirements.txt
```

Make sure the PostgreSQL driver and environment loader are installed:

```powershell
python -m pip install psycopg2-binary python-dotenv
```

Install any other dependencies required by the application.

**Important:** Always install packages using the same Python environment used to execute `app.py`.

---

# 9. Test the Supabase Database Connection

Before starting Flask, verify that Python can connect to Supabase PostgreSQL.

## Step 1: Create a Temporary Python File

Create a file named:

`test_db_connection.py`

Place it in the project root directory.

## Step 2: Add the Following Code

```python
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env", override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")


try:
    connection = psycopg2.connect(
        DATABASE_URL,
        sslmode=os.getenv("DB_SSLMODE", "require")
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            current_database(),
            current_user,
            version();
    """)

    result = cursor.fetchone()

    print("Database connection successful!")
    print("Database:", result[0])
    print("User:", result[1])
    print("PostgreSQL:", result[2])

    cursor.close()
    connection.close()

except Exception as error:
    print("Database connection failed.")
    print(type(error).__name__, error)
```

## Step 3: Execute the Test

Open PowerShell in the project directory.

Run:

```powershell
python test_db_connection.py
```

Expected output:

```text
Database connection successful!
Database: postgres
User: postgres
PostgreSQL: PostgreSQL ...
```

If the connection succeeds, Python is communicating with your Supabase PostgreSQL database.

If the connection fails, verify:

- Database password.
- Database hostname.
- Connection URI.
- SSL configuration.
- Network connectivity.
- Selected connection method.

Delete the temporary test file after completing the connection test if it is no longer required.

---

# 10. Configure the Admin Account

The application uses the PostgreSQL `user_role` enum.

Available roles:

- `admin`
- `user`

To promote an existing registered user to admin:

## Step 1: Open Supabase SQL Editor

1. Open your Supabase project.
2. Navigate to **SQL Editor**.
3. Click **New query**.

## Step 2: Execute the Admin Update Query

Replace the email address with the registered user's email.

```sql
UPDATE public.users
SET role = 'admin'
WHERE email = 'YOUR_REGISTERED_EMAIL';
```

## Step 3: Verify the Updated Account

Execute:

```sql
SELECT
    userid,
    username,
    email,
    role
FROM public.users
WHERE email = 'YOUR_REGISTERED_EMAIL';
```

The user's role should now be `admin`.

Only trusted accounts should receive administrator privileges.

---

# 11. Start the Flask Application

Once the database and Python environment are configured:

1. Activate the virtual environment.
2. Verify that `.env` contains valid local credentials.
3. Confirm that all seven Supabase tables exist.
4. Confirm that the PostgreSQL connection test succeeds.
5. Start the Flask application.

Run:

```powershell
python app.py
```

Open the local URL displayed in the terminal.

Usually:

```text
http://127.0.0.1:5000/
```

### Test the Application Features

Test the following features after starting the application:

- User registration.
- User login.
- Admin login.
- Product listing.
- Product creation.
- Category creation.
- Product editing.
- Product activation and deactivation.
- Add to cart.
- Cart item retrieval.
- Order creation.
- Order details.
- Razorpay test payment.

After each operation, verify that the corresponding records appear in Supabase.

---

# 12. Database Management Through Supabase

The database is managed directly through the Supabase Dashboard.

| Supabase Section | Purpose |
|---|---|
| Table Editor | View and manage database records. |
| SQL Editor | Execute PostgreSQL queries. |
| Database Settings | View database connection information. |
| Logs | Investigate database errors. |
| Backups | Manage available database backups according to your plan. |

### Useful SQL Queries

#### View All Application Tables

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;
```

#### View Users

```sql
SELECT * FROM public.users;
```

#### View Products

```sql
SELECT * FROM public.products;
```

#### View Categories

```sql
SELECT * FROM public.categories;
```

#### View Orders

```sql
SELECT * FROM public.orders;
```

#### View Order Details

```sql
SELECT * FROM public.order_details;
```

#### View Payments

```sql
SELECT * FROM public.payments;
```

#### View Cart Items

```sql
SELECT * FROM public.cart;
```

---

# 13. Row Level Security (RLS)

The current project configuration uses direct PostgreSQL connections from the Flask backend.

RLS is disabled on the application tables in the current setup.

This means database access control is not being enforced through Supabase RLS policies.

### Important Security Considerations

- Never expose the PostgreSQL connection string in frontend code.
- Never expose database credentials to users.
- Keep database operations on the Flask backend.
- Review database access controls before production deployment.
- If RLS is enabled in the future, create and test appropriate policies before relying on it.

Do not confuse Supabase API keys with the PostgreSQL database password.

---

### Before Publishing or Sharing the Repository

- Confirm that `.env` contains placeholders only.
- Never commit actual Supabase passwords.
- Never commit Razorpay secrets.
- Never publish database backups containing private user information.
- Never expose privileged database credentials in frontend code.
- Never include local virtual environment files.

If real credentials were previously committed, replacing them in the latest version does not remove them from Git history.

Rotate exposed credentials and remove sensitive information from Git history where necessary.

---

# 14. Final Setup Checklist

Use this checklist when connecting the application to a new Supabase database.

### Supabase Setup

- [ ] Create a Supabase account.
- [ ] Create an organization.
- [ ] Create a Supabase project.
- [ ] Save the database password securely.
- [ ] Open the SQL Editor.
- [ ] Execute the complete PostgreSQL schema.
- [ ] Verify all seven tables.
- [ ] Verify all five enum types.
- [ ] Verify primary keys and foreign keys.
- [ ] Verify the `updated_at` triggers.

### Database Connection

- [ ] Copy the PostgreSQL connection string.
- [ ] Configure `DATABASE_URL`.
- [ ] Configure `DB_SSLMODE=require`.
- [ ] Verify the connection URI.
- [ ] Test the PostgreSQL connection.

### Python Setup

- [ ] Clone or download the GitHub repository.
- [ ] Create a Python virtual environment.
- [ ] Activate the virtual environment.
- [ ] Install project dependencies.
- [ ] Install `psycopg2-binary`.
- [ ] Install `python-dotenv`.
- [ ] Configure the local `.env` file.

### Application Setup

- [ ] Configure Razorpay test credentials.
- [ ] Start the Flask application.
- [ ] Test user registration and login.
- [ ] Test admin operations.
- [ ] Test product operations.
- [ ] Test category operations.
- [ ] Test cart operations.
- [ ] Test order operations.
- [ ] Test Razorpay test payments.
- [ ] Verify database records in Supabase.

---

# 15. Migration Notes

This repository contains the application-side modifications required to migrate the Flask E-Commerce application from local MySQL to Supabase PostgreSQL.

The original local MySQL database was not modified or deleted.

No existing MySQL records are automatically transferred to Supabase.

Each developer must:

1. Create their own Supabase project.
2. Execute the PostgreSQL schema.
3. Configure their own database credentials.
4. Install the required Python dependencies.
5. Verify the PostgreSQL connection.
6. Configure Razorpay test credentials.
7. Run and test the Flask application.

The application connects to Supabase PostgreSQL using `psycopg2` through a direct backend database connection.

**Database schema management is handled through Supabase. The Flask application does not automatically create or migrate database tables.**
