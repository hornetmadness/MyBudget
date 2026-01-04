"""SQLModel Database Models and Engine Configuration

Defines all database tables and relationships using SQLModel ORM:
- Account: Financial accounts (checking, savings, credit cards, etc.)
- Category: Bill expense categories
- Income: Recurring or one-time income sources
- Bill: Bills and expenses
- Budget: Time-based spending plans
- BudgetBill: Bills associated with specific budgets
- Transactions: All money movements
- ApplicationSettings: App-wide configuration

All models use UUID7 for primary keys and include soft-delete support
via 'deleted' flag. All timestamps are stored in UTC internally.
Timezones are configured via the 'timezone' application setting.
"""

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select
from sqlalchemy import String, TypeDecorator, ForeignKey
from datetime import datetime, timezone, timedelta
from uuid import UUID
from uuid_utils import uuid7
from app.models.schemas import FrequencyEnum, TransactionType, PaymentMethod, UUID7
from app.config import DATABASE_URL
from app.utils import utc_now

# Custom UUID type for SQLite compatibility
class GUID(TypeDecorator):
    """Platform-independent GUID type that uses CHAR(36) in SQLite.
    
    Converts UUID objects to strings for storage and back to UUID
    objects when reading from database.
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif isinstance(value, UUID):
            return str(value)
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return UUID(value)


class Account(SQLModel, table=True):
    """Bank or investment account table.
    
    Represents financial accounts where money is held. Supports various
    account types (checking, savings, credit cards, loans, etc.).
    
    Attributes:
        id: UUID7 primary key
        name: Account name (indexed)
        account_type: JSON string containing type info
        description: Optional account description
        balance: Current account balance
        enabled: Whether account is active
        deleted: Soft delete flag
        created_at: Creation timestamp (stored in UTC)
        updated_at: Last update timestamp (stored in UTC)
    """
    __tablename__ = "account"
    
    id: Optional[UUID7] = Field(default_factory=uuid7, primary_key=True, sa_type=GUID)
    name: str = Field(index=True)
    account_type: str  # JSON stored account type (name and description)
    description: Optional[str] = None
    balance: float = Field(default=0.0)
    enabled: bool = Field(default=True)
    deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Category(SQLModel, table=True):
    """Bill categories for organizing expenses.
    
    Categories help classify and track spending by type (e.g., Utilities,
    Groceries, Entertainment). Names are unique and indexed.
    
    Attributes:
        id: UUID7 primary key
        name: Category name (indexed, unique)
        description: Optional category description
        enabled: Whether category is active
        deleted: Soft delete flag
        created_at: Creation timestamp (stored in UTC)
        updated_at: Last update timestamp (stored in UTC)
    """
    __tablename__ = "category"
    
    id: Optional[UUID7] = Field(default_factory=uuid7, primary_key=True, sa_type=GUID)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    enabled: bool = Field(default=True)
    deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    # Relationships
    bills: List["Bill"] = Relationship(back_populates="category")


class Bill(SQLModel, table=True):
    """Bills linked to an account."""
    __tablename__ = "bill"
    
    id: Optional[UUID7] = Field(default_factory=uuid7, primary_key=True, sa_type=GUID)
    account_id: UUID7 = Field(foreign_key="account.id", sa_type=GUID)
    category_id: Optional[UUID7] = Field(default=None, foreign_key="category.id", sa_type=GUID)
    transfer_account_id: Optional[UUID7] = Field(default=None, foreign_key="account.id", sa_type=GUID)
    name: str = Field(index=True)
    description: Optional[str] = None
    budgeted_amount: float = Field(default=0.0)
    frequency: FrequencyEnum = Field(default=FrequencyEnum.MONTHLY)
    payment_method: PaymentMethod = Field(default=PaymentMethod.MANUAL)
    start_freq: datetime
    enabled: bool = Field(default=True)
    deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    # Relationships
    category: Optional[Category] = Relationship(back_populates="bills")


class Income(SQLModel, table=True):
    """Income sources linked to an account."""
    __tablename__ = "income"
    
    id: Optional[UUID7] = Field(default_factory=uuid7, primary_key=True, sa_type=GUID)
    account_id: UUID7 = Field(foreign_key="account.id", sa_type=GUID)
    name: str = Field(index=True)
    description: Optional[str] = None
    amount: float = Field(default=0.0)
    frequency: FrequencyEnum = Field(default=FrequencyEnum.MONTHLY)
    start_freq: datetime
    enabled: bool = Field(default=True)
    deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Transactions(SQLModel, table=True):
    """Financial transactions for bill payments and account funding."""
    __tablename__ = "transactions"

    id: Optional[UUID7] = Field(default_factory=uuid7, primary_key=True, sa_type=GUID)
    account_id: UUID7 = Field(foreign_key="account.id", sa_type=GUID)
    budgetbill_id: Optional[UUID7] = Field(default=None, foreign_key="budgetbill.id", sa_type=GUID)
    amount: float = Field(default=0.0)
    transaction_type: TransactionType = Field(default=TransactionType.DEBIT)
    occurred_at: datetime = Field(default_factory=utc_now)
    note: Optional[str] = None


class Budget(SQLModel, table=True):
    """Monthly budgets for planning expenses."""
    __tablename__ = "budget"
    
    id: Optional[UUID7] = Field(default_factory=uuid7, primary_key=True, sa_type=GUID)
    name: str = Field(index=True)
    start_date: datetime = Field(default_factory=utc_now)
    end_date: datetime = Field(default_factory=lambda: utc_now() + timedelta(days=15))
    description: Optional[str] = None
    enabled: bool = Field(default=True)
    deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    # Relationships - explicitly define the join condition
    budget_bills: List["BudgetBill"] = Relationship(back_populates="budget")


class BudgetBill(SQLModel, table=True):
    """Junction table linking budgets to bills with specific amounts."""
    __tablename__ = "budgetbill"
    
    id: Optional[UUID7] = Field(default_factory=uuid7, primary_key=True, sa_type=GUID)
    budget_id: UUID7 = Field(foreign_key="budget.id", sa_type=GUID, index=True)
    bill_id: UUID7 = Field(foreign_key="bill.id", sa_type=GUID)
    account_id: UUID7 = Field(foreign_key="account.id", sa_type=GUID)
    transfer_account_id: Optional[UUID7] = Field(default=None, foreign_key="account.id", sa_type=GUID)
    budgeted_amount: float = Field(default=0.0)
    due_date: Optional[datetime] = None
    paid_amount: float = Field(default=0.0)
    paid_on: Optional[datetime] = None
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    # Relationships
    budget: Optional[Budget] = Relationship(back_populates="budget_bills")


class ApplicationSettings(SQLModel, table=True):
    """Application-wide settings - each setting is a separate row."""
    __tablename__ = "application_settings"
    
    id: Optional[UUID7] = Field(default_factory=uuid7, primary_key=True, sa_type=GUID)
    key: str = Field(index=True, unique=True)  # e.g., "currency_symbol", "decimal_places", "number_format"
    value: str  # All values stored as strings
    display_name: str  # Human-readable name for UI display
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


# Database configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True
)


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session
