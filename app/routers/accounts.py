"""Accounts API Router

Provides RESTful API endpoints for account management including:
- CRUD operations (Create, Read, Update, Delete)
- Fund operations (Add, Deduct, Transfer)
- Account balance management
- Transaction recording

All endpoints require database session dependency injection.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime, timezone
from app.models.database import Account, Transactions, get_session
from app.models.schemas import AccountCreate, AccountUpdate, AccountFundOperation, AccountTransferOperation, TransactionType

# Type alias for UUID7
UUID7 = UUID

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=Account)
def create_account(account: AccountCreate, session: Session = Depends(get_session)):
    """Create a new account.
    
    Args:
        account: Account creation data (name, type, description, balance)
        session: Database session (injected)
    
    Returns:
        Created account with generated ID and timestamps
    
    Raises:
        HTTPException: If database operation fails
    """
    db_account = Account.model_validate(account)
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    return db_account


@router.get("/", response_model=list[Account])
def list_accounts(session: Session = Depends(get_session)):
    """Get all accounts.
    
    Args:
        session: Database session (injected)
    
    Returns:
        List of all accounts including enabled and disabled ones
    """
    accounts = session.exec(select(Account)).all()
    return accounts


@router.get("/{account_id}", response_model=Account)
def get_account(account_id: UUID7, session: Session = Depends(get_session)):
    """Get a specific account by ID.
    
    Args:
        account_id: Unique account identifier (UUID7)
        session: Database session (injected)
    
    Returns:
        Account details
    
    Raises:
        HTTPException: 404 if account not found
    """
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.patch("/{account_id}", response_model=Account)
def update_account(
    account_id: UUID7,
    account_update: AccountUpdate,
    session: Session = Depends(get_session),
):
    """Update an account.
    
    Args:
        account_id: Unique account identifier (UUID7)
        account_update: Fields to update (partial update supported)
        session: Database session (injected)
    
    Returns:
        Updated account
    
    Raises:
        HTTPException: 404 if account not found
    """
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Track old balance for transaction creation
    old_balance = account.balance
    
    account_data = account_update.model_dump(exclude_unset=True)
    for key, value in account_data.items():
        setattr(account, key, value)
    
    session.add(account)
    session.commit()
    session.refresh(account)
    
    # Create transaction if balance changed
    new_balance = account.balance
    if old_balance != new_balance:
        balance_change = new_balance - old_balance
        transaction_type = "credit" if balance_change > 0 else "debit"
        
        transaction = Transactions(
            account_id=account.id,
            amount=abs(balance_change),
            transaction_type=transaction_type,
            occurred_at=datetime.now(timezone.utc),
            note="Account balance adjustment",
        )
        session.add(transaction)
        session.commit()
    
    # Ensure all fields are populated in the response
    return Account.model_validate(account, from_attributes=True)


@router.post("/{account_id}/add-funds", response_model=Account)
def add_funds(
    account_id: UUID7,
    operation: AccountFundOperation,
    session: Session = Depends(get_session),
):
    """Add funds to an account and create a credit transaction."""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Add funds to balance
    account.balance += operation.amount
    
    # Create credit transaction
    transaction = Transactions(
        account_id=account.id,
        amount=operation.amount,
        transaction_type=TransactionType.CREDIT,
        occurred_at=datetime.now(timezone.utc),
        note=operation.note or "Funds added to account",
    )
    
    # Commit both changes together
    session.add(account)
    session.add(transaction)
    session.commit()
    session.refresh(account)
    
    return Account.model_validate(account, from_attributes=True)


@router.post("/{account_id}/deduct-funds", response_model=Account)
def deduct_funds(
    account_id: UUID7,
    operation: AccountFundOperation,
    session: Session = Depends(get_session),
):
    """Deduct funds from an account and create a debit transaction."""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.balance < operation.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds in account")
    
    # Deduct funds from balance
    account.balance -= operation.amount
    
    # Create debit transaction
    transaction = Transactions(
        account_id=account.id,
        amount=operation.amount,
        transaction_type=TransactionType.DEBIT,
        occurred_at=datetime.now(timezone.utc),
        note=operation.note or "Funds deducted from account",
    )
    
    # Commit both changes together
    session.add(account)
    session.add(transaction)
    session.commit()
    session.refresh(account)
    
    return Account.model_validate(account, from_attributes=True)


@router.post("/{account_id}/transfer", response_model=dict)
def transfer_funds(
    account_id: UUID7,
    operation: AccountTransferOperation,
    session: Session = Depends(get_session),
):
    """Transfer funds from one account to another and create transaction entries."""
    # Get source account
    source_account = session.get(Account, account_id)
    if not source_account:
        raise HTTPException(status_code=404, detail="Source account not found")
    
    # Get destination account
    dest_account = session.get(Account, operation.to_account_id)
    if not dest_account:
        raise HTTPException(status_code=404, detail="Destination account not found")
    
    # Check sufficient funds
    if source_account.balance < operation.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds in source account")
    
    # Deduct from source
    source_account.balance -= operation.amount
    # Add to destination
    dest_account.balance += operation.amount
    
    # Create debit transaction for source account
    source_transaction = Transactions(
        account_id=source_account.id,
        amount=operation.amount,
        transaction_type=TransactionType.DEBIT,
        occurred_at=datetime.now(timezone.utc),
        note=operation.note or f"Transfer to {dest_account.name}",
    )
    
    # Create credit transaction for destination account
    dest_transaction = Transactions(
        account_id=dest_account.id,
        amount=operation.amount,
        transaction_type=TransactionType.CREDIT,
        occurred_at=datetime.now(timezone.utc),
        note=operation.note or f"Transfer from {source_account.name}",
    )
    
    # Commit all changes
    session.add(source_account)
    session.add(dest_account)
    session.add(source_transaction)
    session.add(dest_transaction)
    session.commit()
    
    return {
        "ok": True,
        "message": f"Transferred ${operation.amount:.2f} from {source_account.name} to {dest_account.name}",
    }


@router.delete("/{account_id}")
def delete_account(account_id: UUID7, session: Session = Depends(get_session)):
    """Delete an account."""
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    session.delete(account)
    session.commit()
    return {"ok": True}
