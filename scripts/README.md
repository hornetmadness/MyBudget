# Loading Sample Data

This directory contains scripts for populating the MyBudget database with sample data.

## Quick Start (Easiest Method)

Run the automated setup script that starts the API and loads data in one command:

```bash
cd /Users/erikmathis/repos/MyBudget
./scripts/setup_and_load.sh
```

This will:
1. Start the API server on `http://localhost:8000`
2. Load comprehensive sample financial data
3. Display API endpoints for exploration

## Manual Setup

### 1. Start the API server

In one terminal, start the FastAPI server:

```bash
cd /Users/erikmathis/repos/MyBudget
python -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 2. Load sample data

In another terminal, run the data loader script:

```bash
cd /Users/erikmathis/repos/MyBudget
python scripts/load_sample_data.py
```

### Sample Output

```
🚀 Starting to load sample data...
📡 API URL: http://localhost:8000

💳 Creating bank accounts...
   ✓ Created: Primary Checking ($15500.75)
   ✓ Created: Emergency Savings ($25000.0)
   ✓ Created: Investment Account ($50000.0)

💰 Creating income accounts...
   ✓ Created: Primary Salary ($5500.0/month)
   ✓ Created: Freelance Work ($1200.0/month)
   ✓ Created: Investment Dividends ($350.0/month)

📊 Creating payment accounts (expense categories)...
   ✓ Created: Housing ($2500.0/month)
   ✓ Created: Utilities ($250.0/month)
   ... and more

📋 Creating bills...
   ✓ Created: Mortgage Payment ($2500.0)
   ✓ Created: Electric Bill ($125.75)
   ... and more

============================================================
✅ Sample data loaded successfully!
============================================================

📈 Summary:
   Bank Accounts: 3
   Income Sources: 3
   Expense Categories: 6
   Bills: 13

💡 Tip: Visit http://localhost:8000/docs to explore the API
```

## Custom API URL

If your API is running on a different host or port:

```bash
python scripts/load_sample_data.py --api-url http://example.com:8000
```

## Scripts Available

### `load_sample_data.py`
**Purpose**: Load sample financial data into the API

**Features**:
- Creates realistic mock financial data via API endpoints
- Supports custom API URLs
- Provides detailed progress output
- Handles errors gracefully
- Can be run multiple times to add additional data

**Usage**:
```bash
python scripts/load_sample_data.py [--api-url URL]
```

### `setup_and_load.sh`
**Purpose**: Automated one-command setup and data loading

**Features**:
- Checks if API is already running
- Starts API server automatically
- Waits for server to be ready
- Loads sample data automatically
- Provides next steps

**Usage**:
```bash
./scripts/setup_and_load.sh
```

## What Gets Loaded

### Bank Accounts (3)
- Primary Checking: $15,500.75
- Emergency Savings: $25,000.00
- Investment Account: $50,000.00

### Income Accounts (3)
- Primary Salary: $5,500/month
- Freelance Work: $1,200/month
- Investment Dividends: $350/month

### Expense Categories / Payment Accounts (6)
- Housing: $2,500/month
- Utilities: $250/month
- Groceries: $600/month
- Transportation: $400/month
- Insurance: $600/month
- Entertainment: $300/month

### Bills (13)
- Mortgage Payment (monthly)
- Electric, Water, Gas Bills (monthly)
- Weekly Groceries
- Gas & Car Maintenance (transportation)
- Health & Auto Insurance (monthly)
- Netflix, Spotify, Gym Membership (monthly)

## Accessing the Data

After loading sample data, you can:

1. **View API Documentation**: http://localhost:8000/docs
2. **View ReDoc**: http://localhost:8000/redoc
3. **Use the API** directly with curl or any HTTP client

Example API calls:

```bash
# Get all bank accounts
curl http://localhost:8000/bank-accounts/

# Get all bills
curl http://localhost:8000/bills/

# Get bills for a specific payment account
curl http://localhost:8000/bills/payment-account/{account_id}

# Get income accounts
curl http://localhost:8000/income-accounts/

# Get payment accounts
curl http://localhost:8000/payment-accounts/
```

## Notes

- The script creates realistic sample financial data
- All timestamps use UTC timezone
- Due dates are set relative to the current date
- Some bills are marked as paid with payment timestamps
- You can run the script multiple times to load additional data

## Resetting Data

To reset the database and start fresh:

1. Stop the API server (Ctrl+C)
2. Delete the `mybudget.db` file in the project root
3. Restart the API server
4. Run the load script again

```bash
rm mybudget.db
python -m uvicorn main:app --reload
# in another terminal:
python scripts/load_sample_data.py
```

## Troubleshooting

### Connection refused error
- Make sure the API server is running on `http://localhost:8000`
- Check if port 8000 is available: `lsof -i :8000`
- Try using a different port: `python -m uvicorn main:app --port 8001`
- Then run: `python scripts/load_sample_data.py --api-url http://localhost:8001`

### Database file already exists
- The script will add data to the existing database
- To start fresh, delete `mybudget.db` before starting the server

### Script permission denied
- Make scripts executable:
  ```bash
  chmod +x scripts/*.sh scripts/*.py
  ```

