"""Income API Router

Provides RESTful API endpoints for income source management including:
- CRUD operations for income sources
- Account-based income tracking
- Recurring income scheduling (frequency-based)
- Soft delete support
- Income verification and deposit logging

Income sources represent regular or one-time money coming into accounts,
such as paychecks, dividends, or gifts. They support various frequencies
for recurring income.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.models.database import Income, Account, get_session
from app.models.schemas import IncomeCreate, IncomeUpdate

router = APIRouter(prefix="/income", tags=["income"])


@router.get("/", response_model=List[dict])
def list_income(session: Session = Depends(get_session)):
    """List all active income sources (excludes soft-deleted).
    
    Args:
        session: Database session (injected)
    
    Returns:
        List of income source dictionaries with id, account_id, name,
        amount, frequency, and other fields. Dates are ISO formatted.
    """
    statement = select(Income).where(Income.deleted == False)
    income_sources = session.exec(statement).all()
    return [
        {
            "id": str(i.id),
            "account_id": str(i.account_id),
            "name": i.name,
            "description": i.description,
            "amount": i.amount,
            "frequency": i.frequency,
            "start_freq": i.start_freq.isoformat() if i.start_freq else None,
            "enabled": i.enabled,
            "created_at": i.created_at.isoformat(),
            "updated_at": i.updated_at.isoformat(),
        }
        for i in income_sources
    ]


@router.get("/{income_id}", response_model=dict)
def get_income(income_id: UUID, session: Session = Depends(get_session)):
    """Get a specific income source by ID.
    
    Args:
        income_id: Unique income source identifier (UUID)
        session: Database session (injected)
    
    Returns:
        Income source dictionary with all fields
    
    Raises:
        HTTPException: 404 if income source not found or is soft-deleted
    """
    income = session.get(Income, str(income_id))
    if not income or income.deleted:
        raise HTTPException(status_code=404, detail="Income not found")
    return {
        "id": str(income.id),
        "account_id": str(income.account_id),
        "name": income.name,
        "description": income.description,
        "amount": income.amount,
        "frequency": income.frequency,
        "start_freq": income.start_freq.isoformat() if income.start_freq else None,
        "enabled": income.enabled,
        "created_at": income.created_at.isoformat(),
        "updated_at": income.updated_at.isoformat(),
    }


@router.get("/account/{account_id}", response_model=List[dict])
def get_income_by_account(account_id: UUID, session: Session = Depends(get_session)):
    """Get all income sources for a specific account."""
    account = session.get(Account, str(account_id))
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    statement = select(Income).where(
        (Income.account_id == account_id) & (Income.deleted == False)
    )
    income_sources = session.exec(statement).all()
    return [
        {
            "id": str(i.id),
            "account_id": str(i.account_id),
            "name": i.name,
            "description": i.description,
            "amount": i.amount,
            "frequency": i.frequency,
            "start_freq": i.start_freq.isoformat() if i.start_freq else None,
            "enabled": i.enabled,
            "created_at": i.created_at.isoformat(),
            "updated_at": i.updated_at.isoformat(),
        }
        for i in income_sources
    ]


@router.post("/", response_model=dict, status_code=201)
def create_income(
    account_id: UUID,
    income_data: IncomeCreate,
    session: Session = Depends(get_session),
):
    """Create a new income source for an account."""
    account = session.get(Account, str(account_id))
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if not account.enabled:
        raise HTTPException(status_code=400, detail="Cannot add income to disabled account")
    
    income = Income(
        account_id=account_id,
        name=income_data.name,
        description=income_data.description,
        amount=income_data.amount,
        frequency=income_data.frequency,
        start_freq=income_data.start_freq,
    )
    
    session.add(income)
    session.commit()
    session.refresh(income)
    
    return {
        "id": str(income.id),
        "account_id": str(income.account_id),
        "name": income.name,
        "description": income.description,
        "amount": income.amount,
        "frequency": income.frequency,
        "start_freq": income.start_freq.isoformat() if income.start_freq else None,
        "enabled": income.enabled,
        "created_at": income.created_at.isoformat(),
        "updated_at": income.updated_at.isoformat(),
    }


@router.patch("/{income_id}", response_model=dict)
def update_income(
    income_id: UUID,
    income_data: IncomeUpdate,
    session: Session = Depends(get_session),
):
    """Update an income source."""
    income = session.get(Income, str(income_id))
    if not income or income.deleted:
        raise HTTPException(status_code=404, detail="Income not found")
    
    # If updating account_id, verify new account exists and is enabled
    if income_data.account_id:
        new_account = session.get(Account, str(income_data.account_id))
        if not new_account:
            raise HTTPException(status_code=404, detail="New account not found")
        if not new_account.enabled:
            raise HTTPException(status_code=400, detail="Cannot move income to disabled account")
    
    income_update_data = income_data.model_dump(exclude_unset=True)
    for key, value in income_update_data.items():
        setattr(income, key, value)
    
    session.add(income)
    session.commit()
    session.refresh(income)
    
    return {
        "id": str(income.id),
        "account_id": str(income.account_id),
        "name": income.name,
        "description": income.description,
        "amount": income.amount,
        "frequency": income.frequency,
        "start_freq": income.start_freq.isoformat() if income.start_freq else None,
        "enabled": income.enabled,
        "created_at": income.created_at.isoformat(),
        "updated_at": income.updated_at.isoformat(),
    }


@router.delete("/{income_id}", status_code=204)
def delete_income(income_id: UUID, session: Session = Depends(get_session)):
    """Soft delete an income source."""
    income = session.get(Income, str(income_id))
    if not income or income.deleted:
        raise HTTPException(status_code=404, detail="Income not found")
    
    income.deleted = True
    session.add(income)
    session.commit()
