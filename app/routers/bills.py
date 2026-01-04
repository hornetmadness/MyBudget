"""Bills API Router

Provides RESTful API endpoints for bill management including:
- CRUD operations for bills
- Account-based bill filtering
- Bill payment tracking
- Recurring bill scheduling

Bills are associated with payment accounts and can be linked to budgets
through the budget bills system.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID
from app.models.database import Bill, Account, get_session
from app.models.schemas import BillCreate, BillUpdate

# Type alias for UUID7
UUID7 = UUID

router = APIRouter(prefix="/bills", tags=["bills"])


@router.post("/{account_id}", response_model=Bill)
def create_bill(account_id: UUID7, bill: BillCreate, session: Session = Depends(get_session)):
    """Create a new bill for a specific account.
    
    Args:
        account_id: Payment account identifier (UUID7)
        bill: Bill creation data (name, amount, frequency, etc.)
        session: Database session (injected)
    
    Returns:
        Created bill with generated ID and timestamps
    
    Raises:
        HTTPException: 404 if account not found
    """
    # Verify account exists
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    db_bill = Bill.model_validate(bill, update={"account_id": account_id})
    session.add(db_bill)
    session.commit()
    session.refresh(db_bill)
    return db_bill


@router.get("/", response_model=list[Bill])
def list_bills(session: Session = Depends(get_session)):
    """Get all bills.
    
    Args:
        session: Database session (injected)
    
    Returns:
        List of all bills across all accounts
    """
    bills = session.exec(select(Bill)).all()
    return bills


@router.get("/{bill_id}", response_model=Bill)
def get_bill(bill_id: UUID7, session: Session = Depends(get_session)):
    """Get a specific bill by ID.
    
    Args:
        bill_id: Unique bill identifier (UUID7)
        session: Database session (injected)
    
    Returns:
        Bill details
    
    Raises:
        HTTPException: 404 if bill not found
    """
    bill = session.get(Bill, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.get("/account/{account_id}", response_model=list[Bill])
def get_bills_by_account(account_id: UUID7, session: Session = Depends(get_session)):
    """Get all bills for a specific account.
    
    Args:
        account_id: Account identifier to filter bills (UUID7)
        session: Database session (injected)
    
    Returns:
        List of bills associated with the account
    
    Raises:
        HTTPException: 404 if account not found
    """
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    bills = session.exec(
        select(Bill).where(Bill.account_id == account_id)
    ).all()
    return bills


@router.patch("/{bill_id}", response_model=Bill)
def update_bill(
    bill_id: UUID7,
    bill_update: BillUpdate,
    session: Session = Depends(get_session),
):
    """Update a bill."""
    bill = session.get(Bill, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    bill_data = bill_update.model_dump(exclude_unset=True)
    for key, value in bill_data.items():
        setattr(bill, key, value)
    
    session.add(bill)
    session.commit()
    session.refresh(bill)
    return bill


@router.delete("/{bill_id}")
def delete_bill(bill_id: UUID7, session: Session = Depends(get_session)):
    """Delete a bill."""
    bill = session.get(Bill, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    session.delete(bill)
    session.commit()
    return {"ok": True}
