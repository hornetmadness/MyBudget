# MyBudget User Guide

**Version 1.0.0**

A simple personal finance management application for tracking accounts, bills, budgets, and transactions.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Application Overview](#application-overview)
3. [Understanding the Flow](#understanding-the-flow)
4. [Tab-by-Tab Guide](#tab-by-tab-guide)
   - [Dashboard](#dashboard)
   - [Accounts](#accounts)
   - [Bills](#bills)
   - [Budgets](#budgets)
   - [Transactions](#transactions)
   - [Reports](#reports)
   - [Settings](#settings)
5. [Common Workflows](#common-workflows)
6. [Tips and Best Practices](#tips-and-best-practices)

---

## Getting Started

MyBudget helps you manage your personal finances by organizing your money into:
- **Accounts**: Where your money lives (checking, savings, credit cards, etc.)
- **Bills**: Regular expenses you need to pay
- **Budgets**: Time-based spending plans
- **Income**: Money coming in
- **Transactions**: Record of all money movements

The application runs in your web browser and stores all data locally on your computer.

---

## Application Overview

### The Big Picture

MyBudget follows a natural financial management flow:

```
1. Set up your ACCOUNTS (where money lives)
   ↓
2. Define your BILLS (what you need to pay)
   ↓
3. Create INCOME SOURCES (money coming in)
   ↓
4. Create a BUDGET (your spending plan for a time period)
   ↓
5. Add bills to your budget
   ↓
6. Track payments and monitor spending on the DASHBOARD
   ↓
7. View complete financial history in TRANSACTIONS
   ↓
8. Analyze spending patterns in REPORTS
```

### Key Concepts

**Accounts**
- Represent real financial accounts (your checking account, savings account, credit cards, etc.)
- Track current balances
- Record all money movements

**Bills**
- Recurring or one-time expenses (rent, utilities, subscriptions)
- Can be associated with specific payment accounts
- Organized by categories (utilities, groceries, entertainment, etc.)

**Budgets**
- Time-based spending plans (e.g., "January 2026 Budget")
- Cannot overlap with other budget periods
- Contain specific bills you plan to pay during that period

**Budget Bills**
- When you add a bill to a budget, it becomes a "budget bill"
- Tracks payment status (unpaid, paid, overdue)
- Shows actual amount paid vs. budgeted amount

**Income Sources**
- Regular or one-time money you expect to receive
- Can be recurring (paychecks, dividends) or one-time (bonuses, gifts)
- Linked to specific deposit accounts
- Track expected vs. actual income

**Transactions**
- Automatic records of all money movements
- Created when you add/deduct funds, transfer money, mark bills as paid, or verify income
- Provides complete financial audit trail

---

## Understanding the Flow

### Initial Setup (First Time Use)

**Quick Start:**
If you're using the bootstrap script, default categories and settings are automatically created for you. Simply run:
```bash
./scripts/setup.sh
```

**Manual Setup:**

1. **Create Your Accounts** (Accounts Tab)
   - Add all your real-world accounts
   - Enter current balances
   - Examples: "Chase Checking", "Capital One Savings", "Discover Card"

2. **Set Up Bills** (Bills Tab)
   - Add recurring bills with payment details
   - Set payment frequency (monthly, weekly, etc.)
   - Choose payment method (manual, automatic)
   - Assign categories to organize expenses

3. **Create Income Sources** (Accounts Tab → Income Section)
   - Add regular income (paychecks, dividends, etc.)
   - Set frequency and amounts
   - Link to deposit accounts

4. **Configure Categories** (Settings Tab)
   - Default categories are created automatically (Housing, Utilities, Transportation, etc.)
   - Create additional custom categories as needed
   - Examples: Utilities, Groceries, Entertainment, Transportation

### Monthly Workflow

1. **Create a New Budget** (Budgets Tab)
   - Name it (e.g., "January 2026")
   - Set start and end dates
   - Optionally clone from previous month

2. **Add Bills to Budget** (Budgets Tab)
   - Select which bills apply to this budget period
   - Adjust amounts if different from usual
   - Set due dates

3. **Monitor Dashboard** (Dashboard Tab)
   - See upcoming bills that need payment
   - Track what's been paid
   - Watch your spending vs. budget

4. **Process Payments**
   - When you pay a bill in real life, mark it as paid in MyBudget
   - The system automatically records the transaction
   - Updates account balances

5. **Log Income** (Accounts Tab)
   - When income arrives, verify it
   - Funds are added to the designated account
   - Transaction is recorded

6. **Review at Month End** (Reports Tab)
   - See where money went
   - Compare to previous months
   - Identify spending patterns

---

## Tab-by-Tab Guide

### Dashboard

**Purpose**: Your command center for daily financial monitoring

**What You See**:
- **Current Budget Overview**: Active budget with total budgeted vs. spent
- **Upcoming Bills**: Bills due soon (color-coded by urgency)
- **Recently Paid**: Bills you've paid recently
- **Expected Income**: Upcoming income deposits

**Key Actions**:
- Click a bill to see details
- Mark bills as paid directly from the dashboard
- Verify income deposits when they arrive
- See budget progress at a glance

**Tips**:
- Check daily to stay on top of due dates
- Red/yellow highlights indicate overdue or due-soon bills
- Green checkmarks show paid bills

---

### Accounts

**Purpose**: Manage all your financial accounts and income sources

#### Accounts Section

**What You Can Do**:
- **Create Account**: Add new bank accounts, credit cards, loans, etc.
- **Edit Account**: Update name, type, or description
- **Add Funds**: Record deposits (manual entry)
- **Deduct Funds**: Record withdrawals or expenses
- **Transfer**: Move money between your accounts
- **View Transactions**: See complete transaction history for an account
- **Enable/Disable**: Toggle account active status

**Account Types Supported**:
- Checking, Savings, Investment, Cash
- Credit Card, Debit Card, Store Card
- Personal Loan, Auto Loan, Student Loan, Mortgage
- Line of Credit, Money Market, Certificate of Deposit
- Retirement Account, Brokerage Account
- Health Savings Account, PayPal, Cryptocurrency Wallet

**Creating an Account**:
1. Click "Create Account"
2. Enter account name (e.g., "Wells Fargo Checking")
3. Select account type
4. Add description (optional)
5. Enter current balance
6. Click "Create"

**Managing Account Funds**:
- **Add Funds**: Use when you deposit cash or receive money
- **Deduct Funds**: Use when you withdraw cash or make a purchase
- **Transfer**: Use when moving money between your accounts (e.g., savings to checking)

#### Income Sources Section

**What You Can Do**:
- **Create Income Source**: Define regular income (paychecks, freelance, dividends)
- **Edit Income**: Update amount, frequency, or account
- **Verify Deposit**: When income arrives, click to record it and add funds to account
- **Delete Income**: Remove income sources no longer applicable

**Creating Income Source**:
1. Click "Create Income Source"
2. Enter income name (e.g., "ABC Corp Paycheck")
3. Select deposit account
4. Enter amount
5. Set frequency using the same frequency types as bills:
   - **Monthly**: Income received once per month (e.g., monthly salary on the 30th)
   - **Biweekly**: Income every 14 days (e.g., biweekly paycheck every other Friday)
   - **Weekly**: Income every 7 days (e.g., weekly freelance payment)
   - **Bimonthly**: Income twice per month (e.g., 1st and 15th of each month)
   - **Daily**: Income received daily (e.g., daily tips, per-diem income)
   - **Once**: One-time income (e.g., bonus, gift, tax refund)
   - **Yearly**: Annual income (e.g., yearly dividend, annual bonus)
   - **Always**: Continuous income stream (e.g., ongoing passive income)
6. Set start date (when you expect first payment) - this determines all future due dates
7. Click "Create"

**How Income Frequency Works**:
- The start date is when you expect the first deposit
- Future expected deposits are calculated automatically based on the frequency
- Dashboard shows upcoming expected income based on the frequency pattern
- Example: Biweekly income starting Jan 5 → expected dates: Jan 5, Jan 19, Feb 2, Feb 16, etc.

**Verifying Income**:
- When income actually arrives, click "Verify Deposit"
- This adds the money to your account and creates a transaction
- Helps track expected vs. actual income

---

### Bills

**Purpose**: Define and manage all your recurring and one-time bills

**What You Can Do**:
- **Create Bill**: Add new expense to track
- **Edit Bill**: Update amount, frequency, or payment details
- **Delete Bill**: Remove bills you no longer pay
- **View All Bills**: See complete list with details

**Creating a Bill**:
1. Click "Create Bill"
2. Enter bill name (e.g., "Electric Company")
3. Select payment account (which account pays this bill)
4. Enter budgeted amount (typical amount you pay)
5. Choose category (helps organize expenses)
6. Set payment frequency:
   - **Monthly**: Bill occurs once per month on a specific day (e.g., rent on the 1st, credit card on the 15th)
   - **Weekly**: Bill occurs every 7 days from the start date (e.g., weekly grocery budget, weekly subscription)
   - **Biweekly**: Bill occurs every 14 days from the start date (e.g., biweekly paychecks, every-other-week bills)
   - **Bimonthly**: Bill occurs twice per month on specific days (e.g., 1st and 15th)
   - **Daily**: Bill occurs every day (e.g., daily parking fees, per-diem expenses)
   - **Once**: One-time expense that doesn't recur (e.g., annual fee, one-time purchase)
   - **Yearly**: Bill occurs once per year on the same date (e.g., annual insurance premium, yearly subscription renewal)
   - **Always**: Continuous or ongoing expense with no specific schedule (e.g., variable utility costs tracked continuously)
   
   **How Frequency Works**:
   - The **start date** you set determines when the first occurrence happens
   - The system calculates future due dates based on the frequency pattern
   - Example: Monthly bill with start date Jan 15 → due dates: Jan 15, Feb 15, Mar 15, etc.
   - Example: Biweekly bill with start date Jan 1 → due dates: Jan 1, Jan 15, Jan 29, Feb 12, etc.
   - Only bills that have a due date within a budget's date range can be added to that budget
7. Select payment method:
   - Manual: You initiate payment
   - Automatic: Auto-drafted from account
   - Transfer: You transfer from another account
8. Add description (optional notes)
9. Click "Create"

**Bill Details**:
- **Frequency**: How often bill recurs
- **Payment Method**: How bill is paid
- **Category**: Expense type for reporting
- **Budgeted Amount**: Planned payment amount
- **Account**: Which account pays this bill

**Important Notes**:
- Bills defined here are templates
- To actually pay them, add them to a budget (see Budgets tab)
- You can have bills not in any budget (future or occasional expenses)

---

### Budgets

**Purpose**: Create time-based spending plans and track actual payments

**The Budget Workflow**:
1. Create a budget for a specific time period
2. Add bills you plan to pay during that period
3. Track payments and compare to budget
4. Analyze spending at period end

#### Creating a Budget

1. Click "Create Budget"
2. Enter budget name (e.g., "January 2026")
3. Select start date (e.g., Jan 1, 2026)
4. Select end date (e.g., Jan 31, 2026)
5. Optionally select a budget to clone from (copies bills from that budget)
6. Click "Create"

**Important**: Budgets cannot overlap. If you try to create a budget that overlaps with an existing one, you'll get an error.

#### Managing Budget Bills

Once a budget is created:

1. **Add Bills to Budget**:
   - Click "Add Bill to Budget"
   - Select a bill from your bills list
   - Adjust the amount if needed (can differ from standard amount)
   - Set due date for this payment
   - Click "Add"
   
   **Important Note**: Only bills whose frequency and start date align with the budget's date range can be added. For example:
   - A monthly bill with start date of the 15th can only be added to budgets that include the 15th
   - A weekly bill can only be added if its recurrence pattern falls within the budget period
   - Bills that don't have a due date during the budget period cannot be added

2. **Edit Budget Bill**:
   - Click edit icon on a budget bill
   - Update amount, due date, or status
   - Save changes

3. **Mark as Paid**:
   - When you pay a bill in real life, click "Mark as Paid"
   - Enter actual amount paid (may differ from budgeted)
   - Select payment account
   - System records transaction and updates account balance

4. **Remove from Budget**:
   - Click delete icon to remove bill from budget
   - Bill template remains (only removes from this budget)

#### Budget Display

**Budget Overview Card**:
- Total Budgeted: Sum of all budget bill amounts
- Total Spent: Sum of all paid amounts
- Remaining: Budget minus spent
- Progress bar: Visual representation

**Budget Bills Table**:
- Bill name and category
- Budgeted amount
- Due date
- Status (Unpaid, Paid, Overdue)
- Actual amount paid (when paid)
- Action buttons (edit, mark paid, delete)

**Color Coding**:
- Red background: Overdue bills
- Yellow background: Due within 3 days
- Green checkmark: Paid bills
- No highlight: Future bills

#### Deleting a Budget

- Click "Delete Budget" button
- Confirm deletion
- Budget bills are removed
- Original bill templates remain unchanged
- Transactions already recorded stay in history

---

### Transactions

**Purpose**: View complete financial history and audit trail

**What You See**:
- Every money movement in your accounts
- Deposits, withdrawals, transfers, bill payments
- All transactions automatically recorded by system

**Transaction Types**:
- **Credit**: Money added (deposits, income, transfers in)
- **Debit**: Money removed (payments, withdrawals, transfers out)

**Viewing Transactions**:
- All transactions listed in one table
- Sortable by date, type, amount, account
- Shows transaction date, type, amount, account, and notes

**Transaction Sources**:
Transactions are created automatically when you:
- Verify an income deposit (CREDIT to account)
- Mark a budget bill as paid (DEBIT from account)
- Add funds to an account (CREDIT)
- Deduct funds from an account (DEBIT)
- Transfer between accounts (DEBIT from source, CREDIT to destination)

**Understanding Transaction Details**:
- **Date**: When transaction occurred
- **Type**: Credit or Debit
- **Amount**: Dollar amount
- **Account**: Which account was affected
- **Note**: Description or reference
- **Source**: What created the transaction (bill payment, manual entry, transfer, etc.)

**No Manual Editing**:
- Transactions are created automatically
- Cannot be edited directly
- Provides accurate audit trail
- If you need to correct something, make an offsetting transaction

---

### Reports

**Purpose**: Analyze spending patterns and compare budget performance

**Features**:

#### Budget Comparison
- Select multiple budgets to compare
- See spending across time periods
- Identify trends and changes

#### Category Analysis
- View spending by category
- See which categories consume most budget
- Track category spending over time

#### Spending Trends
- Visualize spending patterns
- Compare budgeted vs. actual amounts
- Identify areas to reduce spending

**Using Reports**:
1. Select budgets to analyze (single or multiple)
2. Choose report type:
   - Budget overview
   - Category breakdown
   - Trend analysis
3. Review visualizations and tables
4. Export data if needed

**Report Insights**:
- Where is money going?
- Are you staying within budget?
- Which categories are over/under budget?
- How does this month compare to last month?
- What are your spending patterns?

---

### Settings

**Purpose**: Configure application preferences and manage categories

#### Application Settings Sub-Tab

**Currency Format**:
- Set display format for money (e.g., $1,234.56)
- Affects all currency displays throughout app

**Timezone**:
- Set your local timezone for displaying dates and times
- Default: America/New_York
- Affects how budget dates, payment dates, and other timestamps are displayed
- All data is stored internally in UTC (Coordinated Universal Time) for consistency
- Examples: UTC, America/Los_Angeles, Europe/London, Asia/Tokyo, Australia/Sydney

**Category Management**:
- **View Categories**: See all expense categories
- **Create Category**: Add new category for organizing bills
  - Enter name (e.g., "Utilities", "Groceries")
  - Add description (optional)
  - Click "Create"
- **Edit Category**: Update name or description
- **Delete Category**: Remove unused categories
  - Note: Cannot delete if bills use this category

**Common Categories**:
- Housing (rent, mortgage, insurance)
- Utilities (electric, gas, water, internet)
- Transportation (gas, car payment, insurance)
- Food (groceries, dining out)
- Healthcare (insurance, medications, copays)
- Entertainment (streaming, movies, hobbies)
- Personal (clothing, haircuts, gym)
- Debt (credit card payments, loans)

#### Backup Sub-Tab

**Database Backup**:
- Download complete database backup
- Stores all accounts, bills, budgets, and transactions
- Use for safekeeping or moving to another computer

**How to Backup**:
1. Click "Download Backup"
2. Save file to secure location
3. Keep multiple backups in different locations

**Restore Process** (when needed):
- Stop application
- Replace database file with backup
- Restart application

#### About Section

- Application version information
- Quick reference information

---

## Common Workflows

### Setting Up for First Budget

1. **Day 1**: Create all accounts with current balances
2. **Day 2**: Add all recurring bills
3. **Day 3**: Create income sources
4. **Day 4**: Set up expense categories
5. **Day 5**: Create first budget and add bills to it
6. **Going Forward**: Use dashboard daily, create new budgets monthly

### Paying Bills

**Option 1: From Dashboard**
1. See bill in "Upcoming Bills"
2. Pay bill in real life (bank, online, etc.)
3. Click bill to open details
4. Click "Mark as Paid"
5. Confirm amount and account
6. Done - transaction recorded, balance updated

**Option 2: From Budgets Tab**
1. Go to Budgets tab
2. Find bill in budget bills table
3. Click "Mark as Paid" icon
4. Follow same process

### Monthly Budget Creation

**Start of Month**:
1. Go to Budgets tab
2. Click "Create Budget"
3. Name it (e.g., "February 2026")
4. Set date range (Feb 1 - Feb 28)
5. Select previous month to clone from
6. Click "Create"
7. Review cloned bills, adjust amounts if needed
8. Add any new bills for this month
9. Remove any bills not applicable this month

**During Month**:
- Monitor dashboard
- Verify income deposits when they arrive
- Mark bills as paid when you pay them
- Track spending vs. budget
- Reconcile account balances weekly

**End of Month**:
- Ensure all bills marked appropriately
- Review Reports for spending analysis
- Use insights to plan next month

### Tracking Cash Expenses

When you spend cash not linked to a bill:
1. Go to Accounts tab
2. Find your cash account or checking account
3. Click "Deduct Funds"
4. Enter amount spent
5. Add note describing expense (e.g., "Groceries at Walmart")
6. Click "Deduct"

### Managing Multiple Income Sources

1. Create separate income source for each source of income
2. Link each to appropriate deposit account
3. When income arrives, verify each separately
4. Track expected vs. actual amounts

### Handling Unexpected Expenses

**For One-Time Expenses**:
1. Create bill with frequency "Once"
2. Add to current budget
3. Mark as paid when you pay it

**For Emergency Funds**:
1. Keep emergency fund in separate savings account
2. Transfer to checking when needed
3. Use transfer function to record movement

---

## Tips and Best Practices

### Account Management

✅ **DO**:
- Keep account balances accurate
- Reconcile with real bank statements regularly
- Use descriptive account names
- Mark unused accounts as disabled (don't delete)

❌ **DON'T**:
- Delete accounts with transaction history
- Forget to record transfers
- Let balances drift from reality

### Bill Management

✅ **DO**:
- Set realistic budgeted amounts (use averages)
- Use categories consistently
- Update bills when amounts change
- Keep payment methods current

❌ **DON'T**:
- Create duplicate bills
- Forget to update frequency changes
- Delete bills with budget history (disable instead)

### Budget Management

✅ **DO**:
- Create budgets for full months/periods
- Review budget vs. actual regularly
- Clone previous budgets to save time
- Adjust future budgets based on actual spending

❌ **DON'T**:
- Create overlapping budgets
- Forget to mark bills as paid
- Ignore overspending warnings
- Wait until month end to review

### Income Management

✅ **DO**:
- Create income sources for all regular income
- Verify deposits when income actually arrives
- Track expected vs. actual income amounts
- Link income to correct deposit accounts
- Update frequencies when income schedule changes

❌ **DON'T**:
- Forget to verify income deposits
- Assume income will always be the same amount
- Let unverified income accumulate
- Delete income sources with history (disable instead)

### Transaction Tracking

✅ **DO**:
- Let system create transactions automatically
- Review transaction history monthly
- Use notes field for important details
- Keep transactions for historical record

❌ **DON'T**:
- Try to manually edit transactions
- Delete transactions to "fix" mistakes
- Forget that transactions are permanent record

### General Best Practices

1. **Daily**: Check dashboard for upcoming bills and expected income
2. **Weekly**: Verify income deposits, review spending progress
3. **Monthly**: Create next budget, analyze reports, review income vs. expenses
4. **Quarterly**: Review categories, bill amounts, and income sources
5. **Yearly**: Backup database, review annual spending and income trends

### Data Accuracy

- **Reconcile weekly**: Compare app balances to bank balances
- **Verify income promptly**: Confirm deposits when income arrives
- **Record immediately**: Log transactions as they happen
- **Review statements**: Compare to bank statements
- **Track expected income**: Monitor if income arrives on time
- **Fix promptly**: Correct discrepancies right away

### Organization

- **Use consistent naming**: "Chase Checking" not "Chase" or "Checking Chase"
- **Categorize everything**: Assign categories to all bills
- **Add descriptions**: Use description fields for clarity
- **Clean up quarterly**: Review and update outdated information

### Backup Strategy

- **Weekly**: Quick backup to local drive
- **Monthly**: Backup to external drive or cloud
- **Before major changes**: Always backup first
- **Keep multiple versions**: Don't overwrite old backups immediately

---

## Troubleshooting

### Common Issues

**"Account balance doesn't match bank"**
- Review recent transactions for missed entries
- Check for pending transactions not yet recorded
- Look for transfers that weren't logged
- Verify all bill payments were marked

**"Can't create overlapping budget"**
- Check existing budget dates
- Ensure no date overlap exists
- Delete old budget if you want to replace it
- Adjust date ranges to avoid overlap

**"Bill isn't showing in dashboard"**
- Verify bill was added to active budget
- Check that budget is within current date range
- Ensure bill isn't marked as already paid
- Confirm bill due date is upcoming

**"Transaction missing"**
- Verify the action was completed (bill marked paid, funds added, etc.)
- Check if operation failed (error message shown)
- Look in transaction history by date range
- Ensure you're looking at correct account

**"Income not showing up"**
- Verify you clicked "Verify Deposit" on the income source
- Check that income source has correct deposit account
- Look for transaction in Transactions tab
- Ensure income frequency/start date is correct
- Check account balance to confirm deposit was applied

### Getting Help

- Review this user guide for detailed instructions
- Check application settings for configuration issues
- Backup data before making major changes
- Refer to version information in Settings > About

---

## Appendix

### Glossary

- **Account**: A financial account where money is held or owed
- **Bill**: A recurring or one-time expense you need to pay
- **Budget**: A time-based spending plan
- **Budget Bill**: A bill added to a specific budget with payment tracking
- **Category**: An expense classification for organizing bills
- **Credit**: Transaction adding money to an account
- **Debit**: Transaction removing money from an account
- **Income Source**: Regular or one-time money expected to be received
- **Transaction**: A record of money movement

### Keyboard Shortcuts

- Most dialogs: **Esc** to close
- Dropdown menus: Arrow keys to navigate
- Date pickers: Click calendar icon or type YYYY-MM-DD

### Data Files

- Database location: `mybudget.db` in application directory
- Backup files: `.db` files you download
- Never manually edit database file

---

**Last Updated**: January 3, 2026
**Application Version**: 1.0.0

For technical documentation, developers should refer to the inline code documentation and API documentation.
