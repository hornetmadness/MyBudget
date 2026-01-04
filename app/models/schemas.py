"""Pydantic Schemas and Data Models

Defines all Pydantic models used for API request/response validation including:
- Enums for transaction types, frequencies, and payment methods
- Create/Update schemas for all entities (Account, Bill, Budget, etc.)
- Operation schemas for fund transfers and transactions
- Validation rules and constraints

These schemas enforce data integrity at the API boundary and provide
automatic validation, serialization, and OpenAPI documentation.

Key Concepts:
- Create models: Used for POST requests, exclude auto-managed fields
- Update models: Used for PATCH requests, all fields optional
- Operation models: Specialized schemas for specific actions
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

# Shared UUID7 alias used across models
UUID7 = Annotated[UUID, "UUID7"]


class AccountTypeModel(BaseModel):
    """Account type data model.
    
    Represents different types of financial accounts (e.g., Checking,
    Savings, Credit Card, Investment). Used for account categorization.
    
    Attributes:
        name: Account type name
        description: Optional account type description
    """

    name: str
    description: Optional[str] = None


class FrequencyEnum(str, Enum):
    """Frequency options for recurring transactions.
    
    Defines how often bills or income repeat. Used for scheduling
    and payment tracking.
    
    Values:
        ALWAYS: Continuous/unscheduled
        ONCE: One-time occurrence
        DAILY: Every day
        WEEKLY: Every 7 days
        BIWEEKLY: Every 14 days
        BIMONTHLY: Twice per month
        MONTHLY: Once per month
        YEARLY: Once per year
    """
    ALWAYS = "always"
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    BIMONTHLY = "bimonthly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class TransactionType(str, Enum):
    """Direction of a transaction.
    
    Indicates whether money is entering or leaving an account.
    
    Values:
        CREDIT: Money added to an account (deposits, income, transfers in)
        DEBIT: Money removed from an account (payments, withdrawals, transfers out)
    """
    CREDIT = "credit"
    DEBIT = "debit"


class PaymentMethod(str, Enum):
    """Payment method for bills.
    
    Indicates how a bill is paid.
    
    Values:
        MANUAL: Manually paid by user
        AUTOMATIC: Automatically deducted/drafted
        TRANSFER: Paid via account transfer
        OTHER: Other payment method
    """

    MANUAL = "manual"
    AUTOMATIC = "automatic"
    TRANSFER = "transfer"
    OTHER = "other"


class AccountCreate(SQLModel):
    """Account creation schema.
    
    Used for POST /accounts/ endpoint. Excludes auto-managed fields
    like id, created_at, updated_at.
    
    Attributes:
        name: Account name (e.g., "Chase Checking")
        account_type: Type identifier (JSON string)
        description: Optional account description
        balance: Initial balance (default: 0.0)
    """

    name: str
    account_type: str
    description: Optional[str] = None
    balance: float = Field(default=0.0)


class AccountUpdate(SQLModel):
    """Account update schema.
    
    Used for PATCH /accounts/{id} endpoint. All fields optional to
    support partial updates.
    
    Attributes:
        name: Updated account name
        account_type: Updated type identifier
        description: Updated description
        balance: Updated balance
        enabled: Whether account is active
        deleted: Soft delete flag
    """

    name: Optional[str] = None
    account_type: Optional[str] = None
    description: Optional[str] = None
    balance: Optional[float] = None
    enabled: Optional[bool] = None
    deleted: Optional[bool] = None


class AccountFundOperation(SQLModel):
    """Schema for adding or deducting funds from an account.
    
    Used for POST /accounts/{id}/add-funds and deduct-funds endpoints.
    Creates a transaction record.
    
    Attributes:
        amount: Amount to add/deduct (must be positive, >0)
        note: Optional transaction note/description
    """

    amount: float = Field(gt=0, description="Amount to add or deduct (must be positive)")
    note: Optional[str] = None


class AccountTransferOperation(SQLModel):
    """Schema for transferring funds between accounts.
    
    Used for POST /transactions/transfer endpoint. Creates two transaction
    records (debit from source, credit to destination).
    
    Attributes:
        to_account_id: Destination account UUID7
        amount: Amount to transfer (must be positive, >0)
        note: Optional transfer note/description
    """

    to_account_id: UUID7 = Field(description="Destination account ID")
    amount: float = Field(gt=0, description="Amount to transfer (must be positive)")
    note: Optional[str] = None


class CategoryCreate(SQLModel):
    """Category creation schema.
    
    Used for POST /categories/ endpoint. Categories help organize
    bills by type (e.g., Utilities, Groceries).
    
    Attributes:
        name: Category name
        description: Optional category description
    """

    name: str
    description: Optional[str] = None


class CategoryUpdate(SQLModel):
    """Category update model - allows updating specific fields."""

    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    deleted: Optional[bool] = None


class BillCreate(SQLModel):
    """Bill creation schema.
    
    Used for POST /bills/{account_id} endpoint. Bills represent
    recurring or one-time expenses.
    
    Attributes:
        name: Bill name (e.g., "Electric Bill")
        description: Optional bill description
        category_id: Associated category UUID7
        transfer_account_id: Optional transfer account UUID7
        budgeted_amount: Planned/budgeted payment amount
        frequency: Payment frequency (default: MONTHLY)
        payment_method: How bill is paid (default: MANUAL)
        start_freq: First payment date
    """

    name: str
    description: Optional[str] = None
    category_id: Optional[UUID7] = None
    transfer_account_id: Optional[UUID7] = None
    budgeted_amount: float = Field(default=0.0)
    frequency: FrequencyEnum = Field(default=FrequencyEnum.MONTHLY)
    payment_method: PaymentMethod = Field(default=PaymentMethod.MANUAL)
    start_freq: datetime


class BillUpdate(SQLModel):
    """Bill update model - allows updating specific fields."""

    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID7] = None
    transfer_account_id: Optional[UUID7] = None
    budgeted_amount: Optional[float] = None
    frequency: Optional[FrequencyEnum] = None
    payment_method: Optional[PaymentMethod] = None
    start_freq: Optional[datetime] = None
    account_id: Optional[UUID7] = None
    enabled: Optional[bool] = None
    deleted: Optional[bool] = None


class IncomeCreate(SQLModel):
    """Income creation schema.
    
    Used for POST /income/ endpoint. Income sources represent
    recurring or one-time money received.
    
    Attributes:
        name: Income source name (e.g., "Paycheck")
        description: Optional income description
        amount: Expected income amount
        frequency: Income frequency (default: MONTHLY)
        start_freq: First payment date
    """

    name: str
    description: Optional[str] = None
    amount: float = Field(default=0.0)
    frequency: FrequencyEnum = Field(default=FrequencyEnum.MONTHLY)
    start_freq: datetime


class IncomeUpdate(SQLModel):
    """Income update model - allows updating specific fields."""

    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    frequency: Optional[FrequencyEnum] = None
    start_freq: Optional[datetime] = None
    account_id: Optional[UUID7] = None
    enabled: Optional[bool] = None
    deleted: Optional[bool] = None


class TransactionCreate(SQLModel):
    """Transaction creation schema.
    
    Used for POST /transactions/ endpoint. Transactions record all
    money movements.
    
    Attributes:
        account_id: Associated account UUID7
        budgetbill_id: Optional linked budget bill UUID7
        amount: Transaction amount
        transaction_type: CREDIT or DEBIT (default: DEBIT)
        occurred_at: Transaction timestamp (default: now)
        note: Optional transaction note
    """

    account_id: UUID7
    budgetbill_id: Optional[UUID7] = None
    amount: float
    transaction_type: TransactionType = Field(default=TransactionType.DEBIT)
    occurred_at: Optional[datetime] = None
    note: Optional[str] = None


class TransactionUpdate(SQLModel):
    """Transaction update model - allows updating specific fields."""

    budgetbill_id: Optional[UUID7] = None
    amount: Optional[float] = None
    transaction_type: Optional[TransactionType] = None
    occurred_at: Optional[datetime] = None
    note: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BudgetCreate(SQLModel):
    """Budget creation schema.
    
    Used for POST /budgets/ endpoint. Budgets represent time-based
    spending plans. System validates no date overlap with existing budgets.
    
    Attributes:
        name: Budget name (e.g., "January 2026")
        start_date: Budget period start (UTC)
        end_date: Budget period end (UTC)
        description: Optional budget description
    """

    name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None


class BudgetUpdate(SQLModel):
    """Budget update model - allows updating specific fields."""

    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    deleted: Optional[bool] = None


class BudgetBillCreate(SQLModel):
    """Budget-Bill association creation model."""

    bill_id: UUID7
    account_id: UUID7
    transfer_account_id: Optional[UUID7] = None
    budgeted_amount: Optional[float] = None
    due_date: Optional[datetime] = None
    paid_amount: Optional[float] = Field(default=0.0)
    paid_on: Optional[datetime] = None
    note: Optional[str] = None


class BudgetBillUpdate(SQLModel):
    """Budget-Bill association update model."""

    account_id: Optional[UUID7] = None
    transfer_account_id: Optional[UUID7] = None
    budgeted_amount: Optional[float] = None
    due_date: Optional[datetime] = None
    paid_amount: Optional[float] = None
    note: Optional[str] = None
    paid_on: Optional[datetime] = None


class ApplicationSettingRead(SQLModel):
    """Single application setting."""
    key: str
    value: str


class SettingsCreate(SQLModel):
    """Settings creation model - all settings as a dict."""
    currency_symbol: str = "$"
    decimal_places: int = 2
    number_format: str = "comma"  # "comma" or "period"
    show_num_old_budgets: int = 3


class SettingsUpdate(SQLModel):
    """Settings update model - update individual settings."""
    currency_symbol: Optional[str] = None
    decimal_places: Optional[int] = None
    number_format: Optional[str] = None
    show_num_old_budgets: Optional[int] = None
