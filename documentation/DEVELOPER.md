# MyBudget Developer Documentation

**Version 1.0.0**

Comprehensive technical documentation for developers working on MyBudget.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Setup and Installation](#setup-and-installation)
6. [Development Workflow](#development-workflow)
7. [Database Schema](#database-schema)
8. [API Documentation](#api-documentation)
9. [UI Components](#ui-components)
10. [Testing](#testing)
11. [Code Style and Conventions](#code-style-and-conventions)
12. [Common Development Tasks](#common-development-tasks)
13. [Troubleshooting](#troubleshooting)
14. [Contributing](#contributing)

---


## Container Images

Pre-built container images for MyBudget are available on GitHub Container Registry:

- [https://github.com/hornetmadness/MyBudget/pkgs/container/mybudget](https://github.com/hornetmadness/MyBudget/pkgs/container/mybudget)

To pull the latest image:

```bash
docker pull ghcr.io/hornetmadness/mybudget:latest
```

See the link above for available tags and usage instructions.

## Project Overview

MyBudget is a personal finance management application built with a modern Python stack. The application follows a clean separation between backend API (FastAPI), frontend UI (NiceGUI), and data persistence (SQLModel/SQLite).

### Key Features

- **Account Management**: Track multiple financial accounts (checking, savings, credit cards, loans, etc.)
- **Bill Tracking**: Manage recurring and one-time bills with payment tracking
- **Budget Planning**: Create time-based budgets with bill associations and spending analysis
- **Income Management**: Track expected and verified income from multiple sources
- **Transaction Logging**: Automatic transaction recording for all money movements
- **Reporting**: Multi-budget comparison, category analysis, and spending trends

### Design Philosophy

1. **API-First**: All business logic in FastAPI backend, UI is a thin client
2. **Single Source of Truth**: Centralized utilities, no code duplication
3. **Type Safety**: Full type annotations throughout codebase
4. **Automatic Transactions**: System-generated audit trail for all money movements
5. **Soft Deletes**: Data preservation with `deleted` flag instead of hard deletes
6. **Timezone Aware**: All timestamps stored in UTC internally; configurable display timezone via `timezone` setting (default: America/New_York)
6. **Timezone Aware**: All timestamps stored in UTC internally; configurable display timezone via `timezone` setting (default: America/New_York)

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Browser (Client)                     │
│                   http://localhost:8080                  │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   NiceGUI UI Layer                       │
│                   (run_ui.py:8080)                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │  UI Modules (app/ui/modules/)                   │   │
│  │  - dashboard.py  - accounts.py  - bills.py      │   │
│  │  - budgets.py    - transactions.py - reports.py │   │
│  │  - settings.py                                  │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Utilities (app/ui/utils.py)                    │   │
│  │  - fetch functions  - error handling            │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────┐
│                 FastAPI Backend Layer                    │
│                   (main.py:8000)                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Routers (app/routers/)                         │   │
│  │  - accounts.py  - bills.py  - budgets.py        │   │
│  │  - categories.py - income.py - transactions.py  │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Schemas (app/models/schemas.py)                │   │
│  │  - Pydantic models for validation               │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │ SQLModel ORM
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Database Layer (SQLite)                     │
│              (app/models/database.py)                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Tables:                                        │   │
│  │  - Account, Category, Income, Bill              │   │
│  │  - Budget, BudgetBill, Transactions             │   │
│  │  - ApplicationSettings                          │   │
│  └─────────────────────────────────────────────────┘   │
│              File: mybudget.db                           │
└─────────────────────────────────────────────────────────┘
```

### Request Flow Example

```
User clicks "Mark Bill as Paid"
  ↓
UI Module (budgets.py) calls API
  ↓
Router (budgets.py) validates request with Pydantic schema
  ↓
Router creates Transaction record in database
  ↓
Router updates BudgetBill status and amount_paid
  ↓
Router updates Account balance
  ↓
Router returns success response
  ↓
UI refreshes tables and shows success notification
```

### Data Flow Patterns

1. **CRUD Operations**: UI → Router → Database → Response → UI refresh
2. **Fetching Data**: UI utils → API endpoint → Database query → JSON response
3. **Error Handling**: Router error → HTTP response → UI error handler → User notification
4. **Transaction Creation**: Action (pay bill, add funds) → Auto-create Transaction → Update account

---

## Technology Stack

### Backend

- **FastAPI** (≥2.0): Modern async web framework for building APIs
  - Automatic OpenAPI/Swagger documentation
  - Pydantic integration for request/response validation
  - Async request handling
  - Dependency injection

- **SQLModel** (≥0.0.14): SQL database ORM with Pydantic integration
  - Combines SQLAlchemy ORM with Pydantic validation
  - Type-safe database queries
  - Automatic schema generation

- **SQLAlchemy** (≥2.0): Database toolkit and ORM
  - Async support with aiosqlite
  - Connection pooling
  - Transaction management

- **Pydantic** (v2): Data validation using Python type annotations
  - Request/response validation
  - Settings management
  - JSON schema generation

### Frontend

- **NiceGUI** (≥1.4.0): Python-based web UI framework
  - Component-based UI
  - Real-time updates
  - Built on Vue.js and Quasar
  - Server-side Python logic

### Database

- **SQLite**: Lightweight file-based database
  - Single file storage (mybudget.db)
  - No server required
  - ACID compliance
  - Full SQL support

### Development Tools

- **pytest** (≥7.0): Testing framework
- **pytest-httpx** (≥0.21.0): HTTP testing for FastAPI
- **Uvicorn**: ASGI server for FastAPI
- **Python 3.12+**: Modern Python with latest type hints

---

## Project Structure

```
MyBudget/
├── app/
│   ├── config.py                 # Application settings and configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py          # SQLModel ORM models and engine setup
│   │   └── schemas.py           # Pydantic validation schemas
│   ├── routers/                 # FastAPI endpoint routers
│   │   ├── __init__.py
│   │   ├── accounts.py          # Account CRUD + fund operations
│   │   ├── bills.py             # Bill management
│   │   ├── budgets.py           # Budget and BudgetBill operations
│   │   ├── categories.py        # Category management
│   │   ├── income.py            # Income source management
│   │   ├── transactions.py      # Transaction queries
│   │   ├── account_types.py     # Account type definitions
│   │   └── settings.py          # Application settings API
│   └── ui/
│       ├── niceui.py            # NiceGUI UI entry point
│       ├── utils.py             # Centralized fetch and error utilities
│       ├── global_dialogs.py    # Shared dialog components
│       └── modules/             # UI tab modules
│           ├── __init__.py
│           ├── dashboard.py     # Dashboard with budget overview
│           ├── accounts.py      # Account + income management
│           ├── bills.py         # Bill management UI
│           ├── budgets.py       # Budget creation and tracking
│           ├── transactions.py  # Transaction history viewer
│           ├── reports.py       # Analytics and reporting
│           └── settings.py      # Settings and categories
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_accounts.py
│   ├── test_bills.py
│   ├── test_budgets.py
│   ├── test_categories.py
│   ├── test_income.py
│   └── test_transactions.py
├── scripts/                     # Utility scripts
│   ├── bootstrap.py            # Initialize app with defaults (idempotent)
│   ├── bootstrap.sh            # Shell wrapper for bootstrap
│   └── load_sample_data.py     # Load comprehensive test data
├── main.py                      # FastAPI application entry point
├── run_ui.py                    # NiceGUI UI server entry point
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── mybudget.db                  # SQLite database file
├── USER.md                      # User-facing documentation
└── DEVELOPER.md                 # This file
```

### Key Files Explained

#### Backend Entry Points

- **main.py**: FastAPI application factory
  - Registers all routers
  - Configures lifespan events
  - Creates database tables on startup

- **version.txt**: Application version
  - Single source of truth for app versioning
  - Used by CI/CD pipeline for Docker tagging
  - Managed by release-please automation

- **app/config.py**: Centralized configuration
  - Environment variables
  - Application metadata (name, description)
  - Database connection settings
  - Note: Version is now in `version.txt` instead of config

#### Data Models

- **app/models/database.py**: SQLModel ORM models
  - 8 database tables defined as Python classes
  - UUID7 primary keys for distributed systems
  - Soft-delete pattern with `deleted` flag
  - UTC timestamps with automatic updates (configurable via timezone setting)

- **app/utils.py**: Timezone utilities
  - `utc_now()` - Get current time in UTC for storage
  - `get_app_timezone()` - Get ZoneInfo from timezone name
  - `to_utc()` - Convert datetime to UTC
  - `to_app_tz()` - Convert datetime to app's configured timezone

- **app/models/schemas.py**: Pydantic validation schemas
  - Request/response data models
  - Input validation rules
  - Type coercion and serialization
  - Enums for constrained values

#### API Layer

- **app/routers/*.py**: FastAPI routers
  - RESTful endpoint definitions
  - Request validation with Pydantic
  - Business logic implementation
  - Error handling and responses

#### UI Layer

- **run_ui.py**: NiceGUI server initialization
  - Loads UI modules dynamically
  - Configures navigation tabs
  - Handles refresh callbacks

- **app/ui/modules/*.py**: Individual tab implementations
  - Self-contained UI components
  - API interaction logic
  - User event handlers
  - Data display and forms

- **app/ui/utils.py**: Shared utilities
  - `fetch_accounts()`, `fetch_bills()`, `fetch_categories()`, `fetch_transactions()`
  - `handle_error()`: Centralized error formatting
  - Eliminates code duplication

---

## Setup and Installation

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Virtual environment tool (venv, conda, etc.)
- Git (for version control)

### Initial Setup

```bash
# Clone repository (if using version control)
git clone <repository-url>
cd MyBudget

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (done automatically on first run)
# Database will be created at mybudget.db
```

### Quick Start with Bootstrap Script

For a quick setup, use the bootstrap script which starts the API server and initializes the database:

```bash
# On macOS/Linux:
./scripts/setup.sh

# Or run directly with Python:
python scripts/bootstrap.py
```

This will:
1. Start the FastAPI server on port 8000 (if not already running)
2. Initialize database with default categories
3. Verify application settings

### Running the Application

The application requires two servers running simultaneously:

#### Terminal 1: FastAPI Backend

```bash
# Start FastAPI backend on port 8000
uvicorn main:app --reload --port 8000

# Or using fastapi CLI:
fastapi dev main.py --port 8000
```

**Endpoints:**
- API: http://localhost:8000
- Interactive Docs (Swagger): http://localhost:8000/docs
- Alternative Docs (ReDoc): http://localhost:8000/redoc

#### Terminal 2: NiceGUI Frontend

```bash
# Start NiceGUI UI on port 8080
python run_ui.py
```

**Access:**
- Application UI: http://localhost:8080

### Environment Variables

Optional configuration via environment variables:

```bash
# API connection (if backend runs on different host/port)
export API_URL="http://localhost:8000"

# Database connection (PostgreSQL - not fully implemented)
export POSTGRESQL_HOSTNAME="localhost"
export POSTGRESQL_USERNAME="postgres"
export POSTGRESQL_PASSWORD="postgres"
export POSTGRESQL_DATABASE="my_budget"
```

### Database Initialization

On first startup, the application automatically:
1. Creates `mybudget.db` SQLite file
2. Creates all tables with proper schema
3. Sets up indexes for performance

**Manual Database Reset:**
```bash
# Stop both servers
# Delete database file
rm mybudget.db
# Restart servers - fresh database will be created
```

### Bootstrap Script

The bootstrap script (`scripts/bootstrap.py`) initializes the application with essential default data. It is **idempotent** and safe to run multiple times.

**What It Does:**
- Creates 11 default expense categories (Housing, Utilities, Transportation, etc.)
- Initializes application settings with defaults:
  - Currency Symbol: $
  - Decimal Places: 2
  - Number Format: comma
  - Timezone: America/New_York
  - Show Old Budgets: 3
  - Prune Budgets After: 24 months

**Usage:**

```bash
# Ensure FastAPI backend is running on port 8000
uvicorn main:app --reload --port 8000

# In another terminal, run the bootstrap script
python scripts/bootstrap.py

# Or specify a different API URL
python scripts/bootstrap.py --api-url http://localhost:8000

# Or use the shell wrapper (starts API server automatically)
./scripts/bootstrap.sh
```

**Output Example:**
```
🚀 Bootstrapping MyBudget application...
📡 API URL: http://localhost:8000

🏷️  Setting up bill categories...
   ✓ Created: Housing
   ✓ Created: Utilities
   ⊙ Skipped (already exists): Food & Groceries
   ...

⚙️  Verifying application settings...
   ✓ Settings initialized:
      Currency Symbol: $
      Decimal Places: 2
      Number Format: comma
      Timezone: America/New_York
      Show Old Budgets: 3
      Prune Budgets After: 24 months

✅ Bootstrap complete
   Categories: 8 created, 3 already existed
```

### Loading Sample Data

For testing and demonstration purposes, a comprehensive sample data loader is provided at `scripts/load_sample_data.py`.

**What It Creates:**
- **Accounts**: 8 realistic accounts (checking, savings, credit cards, investments)
- **Categories**: 15 expense categories (Utilities, Rent, Groceries, etc.)
- **Income Sources**: Multiple income streams (salary, freelance, investments)
- **Bills**: 20+ recurring bills with various frequencies
- **Budgets**: 3 months of budgets with bills and payments
- **Transactions**: Historical transactions for all payments and income

**Usage:**

```bash
# Ensure FastAPI backend is running on port 8000
uvicorn main:app --reload --port 8000

# In another terminal, run the sample data loader
python scripts/load_sample_data.py

# Or specify a different API URL
python scripts/load_sample_data.py --api-url http://localhost:8000
```

**Output Example:**
```
🚀 Starting to load sample data...
✅ Created 8 accounts
✅ Created 15 categories  
✅ Created 5 income sources
✅ Created 22 bills
✅ Created 3 budgets
✅ Added 45 budget bills
✅ Marked 28 bills as paid
✅ Verified 12 income payments
✅ Loaded sample data
```

**Sample Data Includes:**
- **Monthly Bills**: Rent ($2,100), Electric ($150), Internet ($85)
- **Weekly Bills**: Groceries ($200)
- **Biweekly Bills**: Car Payment ($450)
- **Variable Frequencies**: Subscriptions, memberships, annual fees
- **Accounts with Balances**: Realistic starting balances and transaction history
- **Budget Periods**: Current month plus 2 historical months with payments
- **Income Verification**: Some income marked as received, others pending

**Use Cases:**
- Testing UI with realistic data
- Demonstrating features to stakeholders
- Development and debugging with complex scenarios
- Running edge case tests
- Training new developers

**Cleanup:**
```bash
# To start fresh after loading sample data
rm mybudget.db
# Restart servers for clean database
```

---

## Development Workflow

### Branch Strategy

```
main          Production-ready code
  ├── develop   Integration branch for features
      ├── feature/account-improvements
      ├── feature/budget-cloning
      └── bugfix/transaction-display
```

### Making Changes

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Code Changes**
   - Edit relevant files
   - Follow code style conventions
   - Add/update docstrings

3. **Test Changes**
   ```bash
   # Run all tests
   pytest
   
   # Run specific test file
   pytest tests/test_accounts.py
   
   # Run with coverage
   pytest --cov=app --cov-report=html
   ```

4. **Test Manually**
   - Start both servers
   - Test UI functionality
   - Verify API responses in Swagger docs
   - Check console for errors

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: Add budget cloning functionality"
   ```

6. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub/GitLab
   ```

### Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(accounts): Add transfer between accounts functionality
fix(budgets): Correct budget overlap validation logic
docs(api): Update API endpoint documentation
refactor(ui): Centralize fetch functions in utils.py
test(bills): Add tests for bill payment workflow
```

### Code Review Checklist

Before submitting PR:
- ✅ All tests pass
- ✅ Code follows style conventions
- ✅ Docstrings added/updated
- ✅ No console errors in browser
- ✅ Manual testing completed
- ✅ Database migrations handled (if schema changed)
- ✅ Error handling implemented
- ✅ Type hints present

---

## Database Schema

### Entity Relationship Diagram

```
┌──────────────┐         ┌──────────────┐
│   Account    │◄───────┐│    Income    │
│              │        ││              │
│ id (UUID7)   │        ││ id (UUID7)   │
│ name         │        │└─account_id   │
│ account_type │        │  name         │
│ balance      │        │  amount       │
│ enabled      │        │  frequency    │
└──────┬───────┘        │  start_freq   │
       │                └───────────────┘
       │ pays
       │
       │         ┌──────────────┐
       │         │     Bill     │
       │         │              │
       │         │ id (UUID7)   │
       └────────►│ account_id   │
                 │ category_id  │─────┐
                 │ name         │     │
                 │ amount       │     │
                 │ frequency    │     │
                 └──────┬───────┘     │
                        │             │
                        │ part of     │
                        │             │ categorized by
                 ┌──────▼───────┐     │
                 │    Budget    │     │
                 │              │     │    ┌──────────────┐
                 │ id (UUID7)   │     │    │   Category   │
                 │ name         │     │    │              │
                 │ start_date   │     └───►│ id (UUID7)   │
                 │ end_date     │          │ name         │
                 └──────┬───────┘          │ description  │
                        │                  └──────────────┘
                        │
                        │
                 ┌──────▼───────┐
                 │  BudgetBill  │
                 │              │
                 │ id (UUID7)   │
                 │ budget_id    │
                 │ bill_id      │
                 │ amount       │
                 │ due_date     │
                 │ is_paid      │
                 │ amount_paid  │
                 │ paid_at      │
                 │ paid_from    │─────┐
                 └──────────────┘     │
                                      │ paid from
           ┌──────────────┐           │
           │ Transactions │           │
           │              │           │
           │ id (UUID7)   │◄──────────┘
           │ account_id   │─────────────► Account
           │ budgetbill_id│─────────────► BudgetBill
           │ amount       │
           │ txn_type     │ (CREDIT/DEBIT)
           │ occurred_at  │
           │ note         │
           └──────────────┘

┌────────────────────┐
│ ApplicationSettings│
│                    │
│ id (UUID7)         │
│ key                │
│ value              │
└────────────────────┘
```

### Table Definitions

#### Account

Financial accounts where money is held or owed.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID7 | PRIMARY KEY | Unique identifier |
| name | String | INDEXED | Account name |
| account_type | JSON String | NOT NULL | Account type info |
| description | String | NULLABLE | Optional description |
| balance | Float | DEFAULT 0.0 | Current balance |
| enabled | Boolean | DEFAULT True | Active status |
| deleted | Boolean | DEFAULT False | Soft delete flag |
| created_at | DateTime | AUTO | Creation timestamp (stored in UTC) |
| updated_at | DateTime | AUTO | Last update timestamp (stored in UTC) |

**Indexes:** `ix_account_name`

#### Category

Expense categories for organizing bills.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID7 | PRIMARY KEY | Unique identifier |
| name | String | INDEXED, UNIQUE | Category name |
| description | String | NULLABLE | Optional description |
| enabled | Boolean | DEFAULT True | Active status |
| deleted | Boolean | DEFAULT False | Soft delete flag |
| created_at | DateTime | AUTO | Creation timestamp (stored in UTC) |
| updated_at | DateTime | AUTO | Last update timestamp (stored in UTC) |

**Indexes:** `ix_category_name`

#### Income

Income sources (recurring or one-time).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID7 | PRIMARY KEY | Unique identifier |
| account_id | UUID7 | FOREIGN KEY | Deposit account |
| name | String | NOT NULL | Income source name |
| amount | Float | NOT NULL | Income amount |
| frequency | FrequencyEnum | NOT NULL | How often received |
| start_freq | DateTime | NOT NULL | Start date/time |
| enabled | Boolean | DEFAULT True | Active status |
| deleted | Boolean | DEFAULT False | Soft delete flag |
| created_at | DateTime | AUTO | Creation timestamp (stored in UTC) |
| updated_at | DateTime | AUTO | Last update timestamp (stored in UTC) |

**Relationships:** `account_id` → `Account.id`

#### Bill

Bills and expenses to track.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID7 | PRIMARY KEY | Unique identifier |
| account_id | UUID7 | FOREIGN KEY | Payment account |
| category_id | UUID7 | FOREIGN KEY | Expense category |
| name | String | NOT NULL | Bill name |
| amount | Float | NOT NULL | Budgeted amount |
| frequency | FrequencyEnum | NOT NULL | Payment frequency |
| payment_method | PaymentMethod | NOT NULL | How paid |
| description | String | NULLABLE | Optional description |
| enabled | Boolean | DEFAULT True | Active status |
| deleted | Boolean | DEFAULT False | Soft delete flag |
| created_at | DateTime | AUTO | Creation timestamp (stored in UTC) |
| updated_at | DateTime | AUTO | Last update timestamp (stored in UTC) |

**Relationships:** 
- `account_id` → `Account.id`
- `category_id` → `Category.id`

#### Budget

Time-based spending plans.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID7 | PRIMARY KEY | Unique identifier |
| name | String | NOT NULL | Budget name |
| start_date | DateTime | NOT NULL | Budget start (stored in UTC) |
| end_date | DateTime | NOT NULL | Budget end (stored in UTC) |
| deleted | Boolean | DEFAULT False | Soft delete flag |
| created_at | DateTime | AUTO | Creation timestamp (stored in UTC) |
| updated_at | DateTime | AUTO | Last update timestamp (stored in UTC) |

**Constraints:** No overlapping date ranges allowed

#### BudgetBill

Bills associated with specific budgets.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID7 | PRIMARY KEY | Unique identifier |
| budget_id | UUID7 | FOREIGN KEY | Parent budget |
| bill_id | UUID7 | FOREIGN KEY | Associated bill |
| amount | Float | NOT NULL | Budgeted amount |
| due_date | DateTime | NULLABLE | Due date |
| is_paid | Boolean | DEFAULT False | Payment status |
| amount_paid | Float | DEFAULT 0.0 | Actual amount paid |
| paid_at | DateTime | NULLABLE | Payment timestamp |
| paid_from | UUID7 | FOREIGN KEY | Account used for payment |
| deleted | Boolean | DEFAULT False | Soft delete flag |
| created_at | DateTime | AUTO | Creation timestamp (stored in UTC) |
| updated_at | DateTime | AUTO | Last update timestamp (stored in UTC) |

**Relationships:**
- `budget_id` → `Budget.id`
- `bill_id` → `Bill.id`
- `paid_from` → `Account.id`

#### Transactions

All money movements (audit trail).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID7 | PRIMARY KEY | Unique identifier |
| account_id | UUID7 | FOREIGN KEY | Affected account |
| budgetbill_id | UUID7 | FOREIGN KEY, NULLABLE | Related budget bill |
| amount | Float | NOT NULL | Transaction amount |
| transaction_type | TransactionType | NOT NULL | CREDIT or DEBIT |
| occurred_at | DateTime | NOT NULL | When occurred (stored in UTC) |
| note | String | NULLABLE | Description |
| created_at | DateTime | AUTO | Creation timestamp (stored in UTC) |

**Relationships:**
- `account_id` → `Account.id`
- `budgetbill_id` → `BudgetBill.id`

**Immutable:** Transactions should never be modified or deleted after creation.

#### ApplicationSettings

Key-value store for app-wide settings.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID7 | PRIMARY KEY | Unique identifier |
| key | String | NOT NULL, UNIQUE | Setting key |
| value | String | NOT NULL | Setting value (stored as string) |
| display_name | String | NOT NULL | Human-readable name for UI |
| created_at | DateTime | AUTO | Creation timestamp (stored in UTC) |
| updated_at | DateTime | AUTO | Last update timestamp (stored in UTC) |

**Default Settings:**
- `currency_symbol`: "$" - Currency display symbol
- `decimal_places`: "2" - Decimal places for currency
- `number_format`: "comma" - Number format (comma for 1,234.56 or period for 1.234,56)
- `timezone`: "America/New_York" - App timezone (IANA format, e.g., "UTC", "America/Los_Angeles")
- `prune_budgets_after_months`: "24" - Delete budgets older than this many months
- `show_num_old_budgets`: "3" - Number of old budgets to display

### Enums

#### FrequencyEnum
```python
ALWAYS = "always"     # Continuous/ongoing
ONCE = "once"         # One-time only
DAILY = "daily"       # Every day
WEEKLY = "weekly"     # Every 7 days
BIWEEKLY = "biweekly" # Every 14 days
BIMONTHLY = "bimonthly" # Twice per month
MONTHLY = "monthly"   # Every month
YEARLY = "yearly"     # Every year
```

#### TransactionType
```python
CREDIT = "credit"  # Money added to account
DEBIT = "debit"    # Money removed from account
```

#### PaymentMethod
```python
MANUAL = "manual"         # User initiates payment
AUTOMATIC = "automatic"   # Auto-drafted
TRANSFER = "transfer"     # Transfer from another account
OTHER = "other"           # Other methods
```

---

## API Documentation

### Base URL

```
http://localhost:8000
```

### Authentication

Currently no authentication. Future: JWT tokens or session-based auth.

### Response Format

**Success Response:**
```json
{
  "id": "uuid7-string",
  "field1": "value1",
  "field2": "value2"
}
```

**Error Response:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Endpoints

#### Accounts

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/accounts/` | Create new account |
| GET | `/accounts/` | List all accounts |
| GET | `/accounts/{id}` | Get specific account |
| PATCH | `/accounts/{id}` | Update account |
| DELETE | `/accounts/{id}` | Delete account (soft delete) |
| POST | `/accounts/{id}/add-funds` | Add funds to account |
| POST | `/accounts/{id}/deduct-funds` | Deduct funds from account |
| POST | `/accounts/{id}/transfer` | Transfer to another account |

**Example: Create Account**
```http
POST /accounts/
Content-Type: application/json

{
  "name": "Chase Checking",
  "account_type": "{\"name\": \"Checking\"}",
  "balance": 1500.00,
  "description": "Primary checking account"
}

Response: 201 Created
{
  "id": "01234567-89ab-cdef-0123-456789abcdef",
  "name": "Chase Checking",
  "account_type": "{\"name\": \"Checking\"}",
  "balance": 1500.00,
  "description": "Primary checking account",
  "enabled": true,
  "deleted": false,
  "created_at": "2026-01-03T10:30:00Z",
  "updated_at": "2026-01-03T10:30:00Z"
}
```

**Example: Add Funds**
```http
POST /accounts/{id}/add-funds
Content-Type: application/json

{
  "amount": 500.00,
  "note": "Paycheck deposit"
}

Response: 200 OK
{
  "id": "01234567-89ab-cdef-0123-456789abcdef",
  "balance": 2000.00,
  "transaction_id": "transaction-uuid"
}
```

#### Bills

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/bills/` | Create new bill |
| GET | `/bills/` | List all bills |
| GET | `/bills/{id}` | Get specific bill |
| PATCH | `/bills/{id}` | Update bill |
| DELETE | `/bills/{id}` | Delete bill (soft delete) |
| GET | `/bills/by-account/{account_id}` | Get bills for account |

**Example: Create Bill**
```http
POST /bills/
Content-Type: application/json

{
  "name": "Electric Bill",
  "account_id": "account-uuid",
  "category_id": "category-uuid",
  "amount": 125.50,
  "frequency": "monthly",
  "payment_method": "automatic",
  "description": "Electric utility"
}

Response: 201 Created
```

#### Budgets

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/budgets/` | Create new budget |
| GET | `/budgets/` | List all budgets |
| GET | `/budgets/{id}` | Get specific budget |
| DELETE | `/budgets/{id}` | Delete budget |
| POST | `/budgets/{id}/bills` | Add bill to budget |
| GET | `/budgets/{id}/bills` | Get budget bills |
| PATCH | `/budgets/{id}/bills/{bill_id}` | Update budget bill |
| DELETE | `/budgets/{id}/bills/{bill_id}` | Remove bill from budget |
| POST | `/budgets/{id}/bills/{bill_id}/pay` | Mark budget bill as paid |

**Example: Create Budget**
```http
POST /budgets/
Content-Type: application/json

{
  "name": "January 2026",
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z"
}

Response: 201 Created
```

**Example: Mark Bill as Paid**
```http
POST /budgets/{budget_id}/bills/{budgetbill_id}/pay
Content-Type: application/json

{
  "amount_paid": 125.50,
  "paid_from": "account-uuid"
}

Response: 200 OK
# Creates transaction automatically
```

#### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/categories/` | Create new category |
| GET | `/categories/` | List all categories |
| GET | `/categories/{id}` | Get specific category |
| PATCH | `/categories/{id}` | Update category |
| DELETE | `/categories/{id}` | Delete category (soft delete) |

#### Income

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/income/` | Create income source |
| GET | `/income/` | List all income sources |
| GET | `/income/{id}` | Get specific income |
| PATCH | `/income/{id}` | Update income |
| DELETE | `/income/{id}` | Delete income (soft delete) |

#### Transactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/transactions/` | List all transactions |
| GET | `/transactions/{id}` | Get specific transaction |
| GET | `/transactions/by-account/{account_id}` | Get account transactions |

**Note:** Transactions are created automatically by the system. No POST/PATCH/DELETE endpoints.

### Swagger Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## UI Components

### Module Structure

Each UI module in `app/ui/modules/` follows this pattern:

```python
"""Module docstring explaining purpose."""

from app.ui.utils import fetch_accounts, fetch_bills, handle_error

def build_<module>_tab(ui, requests, API_URL, *args):
    """Build the module UI.
    
    Args:
        ui: NiceGUI ui instance
        requests: HTTP requests module
        API_URL: Backend API base URL
        *args: Additional dependencies
    """
    # State variables
    data = []
    
    # Helper functions
    def fetch_data():
        """Fetch data from API."""
        resp = requests.get(f"{API_URL}/endpoint")
        if resp.status_code == 200:
            return resp.json()
        return []
    
    def refresh():
        """Refresh UI with latest data."""
        nonlocal data
        data = fetch_data()
        table.rows = data
    
    # Event handlers
    def handle_create():
        """Handle create button click."""
        # Open dialog
        pass
    
    def handle_edit(e):
        """Handle edit action."""
        # Open dialog with existing data
        pass
    
    # UI Components
    with ui.row():
        ui.button("Create", on_click=handle_create)
    
    table = ui.table(
        columns=[...],
        rows=[]
    )
    
    # Wire up events
    table.on('edit', handle_edit)
    
    # Initial data load
    refresh()
```

### Common UI Patterns

#### Creating Dialogs

```python
dialog = ui.dialog()

with dialog, ui.card():
    ui.label("Dialog Title")
    name_input = ui.input("Name")
    amount_input = ui.number("Amount")
    
    with ui.row():
        ui.button("Cancel", on_click=dialog.close)
        ui.button("Submit", on_click=lambda: submit_and_close())

def submit_and_close():
    # Validate inputs
    # Make API call
    resp = requests.post(f"{API_URL}/endpoint", json={...})
    if resp.status_code == 200:
        ui.notify("Success!", type="positive")
        dialog.close()
        refresh()
    else:
        ui.notify(handle_error(resp), type="negative")
```

#### Data Tables

```python
columns = [
    {"name": "name", "label": "Name", "field": "name", "align": "left"},
    {"name": "amount", "label": "Amount", "field": "amount", "align": "right"},
    {"name": "actions", "label": "Actions", "field": "actions"},
]

def create_row(item):
    """Transform data item into table row."""
    return {
        "id": item["id"],
        "name": item["name"],
        "amount": f"${item['amount']:,.2f}",
        "actions": ""  # Action buttons added via slot
    }

rows = [create_row(item) for item in data]

table = ui.table(columns=columns, rows=rows)

# Add action buttons via slot
table.add_slot('body-cell-actions', '''
    <q-td :props="props">
        <q-btn icon="edit" @click="$parent.$emit('edit', props.row)" />
        <q-btn icon="delete" @click="$parent.$emit('delete', props.row)" />
    </q-td>
''')

# Handle events
table.on('edit', handle_edit)
table.on('delete', handle_delete)
```

#### Error Handling

```python
from app.ui.utils import handle_error

resp = requests.post(f"{API_URL}/endpoint", json=payload)
if resp.status_code != 200:
    ui.notify(handle_error(resp), type="negative")
    return

# Success
ui.notify("Operation successful!", type="positive")
```

#### Fetching Data

```python
from app.ui.utils import fetch_accounts, fetch_bills, fetch_categories

# Instead of duplicating fetch logic:
accounts = fetch_accounts(requests, API_URL)
bills = fetch_bills(requests, API_URL)
categories = fetch_categories(requests, API_URL)
```

### Refresh Callbacks

To allow modules to refresh each other:

```python
# In run_ui.py or module:
_refresh_dashboard_ref = [None]

def register_refresh_callback(callback):
    _refresh_dashboard_ref[0] = callback

# In dashboard module:
register_refresh_callback(refresh_dashboard_data)

# In other modules, trigger refresh:
if _refresh_dashboard_ref[0]:
    _refresh_dashboard_ref[0]()
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_accounts.py

# Run specific test
pytest tests/test_accounts.py::test_create_account

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Structure

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.database import get_session, SQLModel, create_engine
from sqlmodel import Session

# Test fixtures
@pytest.fixture(name="session")
def session_fixture():
    """Create test database session."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with test database."""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

# Test cases
def test_create_account(client: TestClient):
    """Test creating a new account."""
    response = client.post(
        "/accounts/",
        json={
            "name": "Test Account",
            "account_type": '{"name": "Checking"}',
            "balance": 100.0
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Account"
    assert data["balance"] == 100.0

def test_list_accounts(client: TestClient):
    """Test listing accounts."""
    # Create test data
    client.post("/accounts/", json={...})
    
    # Test list endpoint
    response = client.get("/accounts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
```

### Test Coverage Goals

- **Routers**: 90%+ coverage
- **Models**: 100% coverage
- **Critical paths**: 100% coverage (payments, transactions, balance updates)
- **UI**: Manual testing (automated UI testing is complex with NiceGUI)

### Manual Testing Checklist

- [ ] Create account
- [ ] Edit account
- [ ] Add/deduct funds
- [ ] Transfer between accounts
- [ ] Create bill
- [ ] Create budget
- [ ] Add bill to budget
- [ ] Mark bill as paid
- [ ] Verify transaction created
- [ ] Check account balance updated
- [ ] Create income source
- [ ] Verify income deposit
- [ ] View transaction history
- [ ] Generate reports
- [ ] Export/backup data

---

## Code Style and Conventions

### Python Style

Follow **PEP 8** and **PEP 484** (type hints):

```python
# Good
def calculate_total(amount: float, tax_rate: float = 0.08) -> float:
    """Calculate total with tax.
    
    Args:
        amount: Base amount before tax
        tax_rate: Tax rate as decimal (default 8%)
    
    Returns:
        Total amount including tax
    """
    return amount * (1 + tax_rate)

# Bad
def calc(a, t=0.08):
    return a*(1+t)
```

### Type Hints

Use type hints everywhere:

```python
from typing import Optional, List, Dict, Tuple

def fetch_accounts() -> List[Dict[str, any]]:
    """Fetch all accounts."""
    ...

def update_account(id: str, name: str) -> Tuple[bool, Optional[str]]:
    """Update account, return (success, error_message)."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def complex_function(param1: str, param2: int, param3: bool = False) -> Dict[str, any]:
    """One-line summary.
    
    Detailed description of what the function does,
    spanning multiple lines if needed.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        param3: Description of optional parameter (default: False)
    
    Returns:
        Dictionary containing result data with keys:
            - 'status': Operation status
            - 'data': Result data
    
    Raises:
        ValueError: If param2 is negative
        HTTPError: If API request fails
    
    Examples:
        >>> result = complex_function("test", 42)
        >>> print(result['status'])
        'success'
    """
```

### Naming Conventions

- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

```python
# Constants
API_URL = "http://localhost:8000"
MAX_RETRIES = 3

# Classes
class AccountManager:
    pass

# Functions and variables
def fetch_user_accounts(user_id: str) -> List[Account]:
    account_list = []
    return account_list

# Private
def _internal_helper():
    pass
```

### File Organization

1. Module docstring
2. Imports (stdlib, third-party, local)
3. Constants
4. Classes
5. Functions
6. Main execution

```python
"""Module for account management."""

# Standard library
import json
from datetime import datetime
from typing import List, Optional

# Third-party
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select

# Local
from app.models.database import Account
from app.models.schemas import AccountCreate

# Constants
DEFAULT_CURRENCY = "USD"

# Classes
class AccountService:
    ...

# Functions
def create_account(...):
    ...

# Main (if script)
if __name__ == "__main__":
    ...
```

### Error Handling

```python
# Good - Specific exceptions with helpful messages
try:
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(
            status_code=404,
            detail=f"Account with ID {account_id} not found"
        )
except SQLAlchemyError as e:
    raise HTTPException(
        status_code=500,
        detail=f"Database error: {str(e)}"
    )

# Bad - Bare except, generic message
try:
    account = session.get(Account, account_id)
except:
    raise HTTPException(status_code=500, detail="Error")
```

### Code Comments

```python
# Good - Explain WHY, not WHAT
# Use UUID7 instead of UUID4 for better database indexing performance
account_id = uuid7()

# Calculate tax before discount because promotions apply to pre-tax amount
tax = subtotal * tax_rate
total = (subtotal + tax) - discount

# Bad - Obvious comments
# Create a variable
x = 10

# Add 1 to x
x = x + 1
```

---

## Timezone Management

### Overview

MyBudget is timezone-aware. All timestamps are stored in **UTC internally** for consistency and database integrity. The app's display timezone is configured via the `timezone` application setting (default: `America/New_York`).

### Timezone Utilities

The `app/utils.py` module provides timezone helper functions:

```python
from app.utils import utc_now, to_utc, to_app_tz, get_app_timezone

# Get current time in UTC (for storage)
now_utc = utc_now()  # Returns: datetime in UTC

# Get ZoneInfo timezone object
ny_tz = get_app_timezone("America/New_York")

# Convert to UTC (for storage)
utc_dt = to_utc(some_datetime)

# Convert to app timezone (for display)
app_dt = to_app_tz(utc_dt, "America/New_York")
```

### Best Practices

1. **Always store timestamps in UTC:**
   ```python
   from app.utils import utc_now
   
   # In database models, use utc_now() as default factory
   created_at: datetime = Field(default_factory=utc_now)
   ```

2. **Use to_utc() when receiving user input:**
   ```python
   from app.utils import to_utc
   
   # Convert any user-provided datetime to UTC
   payment_date = to_utc(budget_bill_update.paid_on)
   ```

3. **Assume naive datetimes are UTC:**
   - If a datetime has no timezone info (naive), it's treated as UTC
   - The `to_utc()` function automatically adds UTC timezone to naive datetimes

4. **Frontend displays use app timezone:**
   - The UI loads the `timezone` setting and uses it for display
   - Conversion to display timezone happens on the client side when needed

### Application Setting

The `timezone` setting is configurable via the Settings tab in the UI:

- **Key:** `timezone`
- **Default Value:** `America/New_York`
- **Format:** IANA timezone name (e.g., "UTC", "America/Los_Angeles", "Europe/London")
- **Supported Timezones:** Any valid IANA timezone (Python 3.9+ with zoneinfo)

### Example: Adding a New Timestamp Field

```python
from app.models.database import SQLModel, Field
from app.utils import utc_now

class MyModel(SQLModel, table=True):
    id: UUID7 = Field(default_factory=uuid7, primary_key=True)
    name: str
    # Timestamps always use utc_now()
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
```

---

## Common Development Tasks

### Adding a New Table

1. **Define SQLModel in database.py:**
```python
class NewTable(SQLModel, table=True):
    """Description of table."""
    id: UUID = Field(default_factory=UUID7, primary_key=True)
    name: str = Field(index=True)
    value: float
    deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

2. **Create Pydantic schemas in schemas.py:**
```python
class NewTableCreate(BaseModel):
    name: str
    value: float

class NewTableUpdate(BaseModel):
    name: Optional[str] = None
    value: Optional[float] = None
```

3. **Create router in routers/:**
```python
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.models.database import NewTable, get_session
from app.models.schemas import NewTableCreate, NewTableUpdate

router = APIRouter(prefix="/newtable", tags=["newtable"])

@router.post("/")
def create_item(item: NewTableCreate, session: Session = Depends(get_session)):
    db_item = NewTable(**item.model_dump())
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.get("/")
def list_items(session: Session = Depends(get_session)):
    items = session.exec(select(NewTable).where(NewTable.deleted == False)).all()
    return items
```

4. **Register router in main.py:**
```python
from app.routers import newtable
app.include_router(newtable.router)
```

5. **Delete database to recreate schema:**
```bash
rm mybudget.db
# Restart servers
```

6. **Add tests:**
```python
def test_create_newtable(client: TestClient):
    response = client.post("/newtable/", json={"name": "Test", "value": 10.0})
    assert response.status_code == 200
```

### Adding a New UI Module

1. **Create module file in app/ui/modules/:**
```python
# app/ui/modules/newfeature.py
"""New Feature Module."""

def build_newfeature_tab(ui, requests, API_URL, *args):
    """Build the new feature tab."""
    ui.label("New Feature")
    # Add UI components
```

2. **Register in run_ui.py:**
```python
from app.ui.modules import newfeature

# In tab registration
tabs["New Feature"] = newfeature.build_newfeature_tab
```

3. **Add to navigation:**
Module will automatically appear as a tab.

### Adding a New API Endpoint

1. **Add function to appropriate router:**
```python
@router.post("/{id}/custom-action")
def custom_action(
    id: UUID,
    data: CustomActionSchema,
    session: Session = Depends(get_session)
):
    """Perform custom action on resource."""
    resource = session.get(Resource, id)
    if not resource:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Perform action
    resource.field = data.value
    session.add(resource)
    session.commit()
    session.refresh(resource)
    return resource
```

2. **Add schema if needed:**
```python
class CustomActionSchema(BaseModel):
    value: str
```

3. **Add test:**
```python
def test_custom_action(client: TestClient):
    # Create resource
    create_resp = client.post("/resource/", json={...})
    resource_id = create_resp.json()["id"]
    
    # Test action
    response = client.post(
        f"/resource/{resource_id}/custom-action",
        json={"value": "test"}
    )
    assert response.status_code == 200
```

### Database Migration (Manual)

Currently no automatic migration tool. To update schema:

1. **Backup current database:**
```bash
cp mybudget.db mybudget_backup.db
```

2. **Update models in database.py**

3. **Option A - Fresh start (loses data):**
```bash
rm mybudget.db
# Restart servers
```

4. **Option B - Manual migration:**
```python
# Create migration script
from sqlmodel import Session, create_engine
from app.models.database import Account

engine = create_engine("sqlite:///mybudget.db")

with Session(engine) as session:
    # Add new column manually
    session.exec("ALTER TABLE account ADD COLUMN new_field VARCHAR")
    session.commit()
```

**Future:** Integrate Alembic for automatic migrations.

---

## Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
# Ensure you're in project root
pwd  # Should show /path/to/MyBudget

# Ensure virtual environment is activated
which python  # Should show .venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

#### Database locked errors
```bash
# Stop both servers
# Delete database
rm mybudget.db
# Restart servers
```

#### Port already in use
```bash
# Find process using port
lsof -i :8000  # or :8080

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001
```

#### UI not updating after API changes
```bash
# Hard refresh browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
# Or clear browser cache
```

#### Import errors in tests
```bash
# Ensure pytest is installed
pip install pytest pytest-httpx

# Run from project root
cd /path/to/MyBudget
pytest
```

#### Transaction not created
- Check that endpoint creates Transaction record
- Verify account_id is valid
- Check occurred_at is set
- Look for errors in FastAPI logs

#### Balance not updating
- Verify transaction amount is correct
- Check transaction_type (CREDIT vs DEBIT)
- Ensure account.balance calculation is correct
- Check for database commit() calls

### Debug Mode

Enable debug logging:

```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or for specific logger
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)
```

View FastAPI logs:
```bash
# Terminal running uvicorn will show request logs
# Look for status codes, errors, stack traces
```

### Performance Issues

- **Slow queries**: Add database indexes
- **Memory issues**: Reduce data fetching, add pagination
- **Slow UI**: Debounce refresh calls, lazy load data

---

## Contributing

### Getting Started

1. Fork repository
2. Clone your fork
3. Create feature branch
4. Make changes
5. Write tests
6. Submit pull request

### Pull Request Process

1. **Update documentation** if adding features
2. **Add tests** for new functionality
3. **Ensure tests pass**: `pytest`
4. **Follow code style** conventions
5. **Write clear commit messages**
6. **Update CHANGELOG** (if exists)

### Code Review Guidelines

Reviewers check for:
- Code correctness
- Test coverage
- Documentation completeness
- Style compliance
- Security considerations
- Performance implications

---

## CI/CD Pipeline

### GitHub Actions Workflow (`.github/workflows/ci.yml`)

The project uses GitHub Actions for automated testing and deployment.

**Trigger Events:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual trigger via workflow_dispatch

**Jobs:**

#### 1. Test Job
- **Runs on:** Ubuntu latest
- **Steps:**
  - Checkout code
  - Set up Python 3.12
  - Install dependencies from `requirements.txt`
  - Run pytest: `pytest --tb=short -v`
- **Output:** Test results and coverage
- **Runs on:** All push/PR events

#### 2. Build and Push Job
- **Runs on:** Ubuntu latest
- **Dependencies:** Requires `test` job to pass
- **Triggers on:** Push to main/develop only (not PRs)
- **Steps:**
  - Checkout code
  - Set up Docker Buildx
  - Extract version from `version.txt`
  - Log in to GitHub Container Registry (GHCR)
  - Extract Docker metadata (tags, labels)
  - Build and push image to GHCR: `ghcr.io/hornetmadness/mybudget`
  - Output image URL to workflow summary
- **Image Tags:**
  - `latest` (on default branch push)
  - `<version>` (from version.txt, on default branch)
  - `<branch>` (branch name)
  - `<sha>` (commit SHA)

### Version Management

**Version Source of Truth:** `version.txt`

The CI workflow reads the version directly from `version.txt` for Docker image tagging:
```bash
VERSION=$(cat version.txt)
```

This ensures the Docker image version always matches the application version configured in `version.txt`.

### Docker Image Registry

- **Registry:** GitHub Container Registry (GHCR)
- **Image:** `ghcr.io/hornetmadness/mybudget`
- **Authentication:** Uses `GITHUB_TOKEN` (automatically available in GitHub Actions)
- **Access:** Requires GitHub account with appropriate permissions

### Local CI Testing

To test the CI pipeline locally before pushing:

```bash
# Run tests
pytest --tb=short -v

# Build Docker image locally
docker build -t mybudget:local .

# Tag with version from version.txt
VERSION=$(cat version.txt)
docker tag mybudget:local mybudget:$VERSION
```

---

### Release Process

The project uses [release-please](https://github.com/googleapis/release-please) for automated versioning and releases.

**Version Source of Truth**: `version.txt` (previously `app/config.py`)

**Release Workflow**:
1. Commit changes to `main` branch
2. release-please automatically creates a PR with:
   - Updated `version.txt`
   - Updated `.release-please-manifest.json`
   - Changelog entries
3. Merge the release PR
4. GitHub Actions CI workflow automatically:
   - Runs tests
   - Builds Docker image with version tag from `version.txt`
   - Publishes image to GHCR (ghcr.io/hornetmadness/mybudget)
   - Creates a GitHub Release

**Manual Override** (if needed):
- Edit `version.txt` directly
- Update `.release-please-manifest.json` to match
- Push changes; release-please will respect the change on next run

**Version Tag Format**: `v0.1.0` (automatically created from semantic versioning)

---

## Appendix

### Useful Commands

```bash
# Database inspection
sqlite3 mybudget.db
.tables
.schema account
SELECT * FROM account;

# Python REPL with app context
python -i
>>> from app.models.database import *
>>> from sqlmodel import Session, create_engine, select
>>> engine = create_engine("sqlite:///mybudget.db")
>>> session = Session(engine)
>>> accounts = session.exec(select(Account)).all()

# API testing with curl
curl http://localhost:8000/accounts/
curl -X POST http://localhost:8000/accounts/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","account_type":"{\"name\":\"Checking\"}","balance":100}'

# Package management
pip list  # Show installed packages
pip freeze > requirements.txt  # Update requirements
pip install -r requirements.txt  # Install from requirements
```

### Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **NiceGUI Docs**: https://nicegui.io/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Python Type Hints**: https://docs.python.org/3/library/typing.html

### Architecture Decisions

**Why FastAPI?**
- Automatic API documentation
- Async support for performance
- Strong typing with Pydantic
- Modern Python features

**Why SQLModel?**
- Combines SQLAlchemy + Pydantic
- Single model definition for DB and API
- Type safety across layers

**Why NiceGUI?**
- Python-based UI (no JavaScript needed)
- Real-time updates
- Fast prototyping
- Server-side logic

**Why SQLite?**
- No server setup required
- Single file database
- Sufficient for personal finance app
- Easy backup/restore

**Why UUID7?**
- Better database indexing than UUID4
- Sortable by creation time
- Distributed system ready

**Why Soft Deletes?**
- Data preservation for audit trail
- Easier to recover from mistakes
- Historical reporting intact

---

**Last Updated**: January 3, 2026
**Application Version**: 1.0.0
**Document Version**: 1.0

For user-facing documentation, see [USER.md](USER.md).
