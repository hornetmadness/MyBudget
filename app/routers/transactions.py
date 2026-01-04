"""Transactions API Router

Provides RESTful API endpoints for transaction management including:
- Transaction CRUD operations
- Account-based transaction filtering
- Budget bill transaction tracking
- Transfer operations between accounts
- Transaction type classification (credit/debit)

Transactions represent all money movements including deposits, withdrawals,
transfers, and bill payments. They maintain complete financial history
and are linked to accounts and optionally to budget bills.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID
from app.models.database import (
    Transactions,
    Account,
    BudgetBill,
    get_session,
)

# Type alias for UUID7
UUID7 = UUID

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _ensure_account(session: Session, account_id: UUID7) -> Account:
    """Verify account exists and return it.
    
    Args:
        session: Database session
        account_id: Account identifier to verify
    
    Returns:
        Account object if found
    
    Raises:
        HTTPException: 404 if account not found
    """
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


def _ensure_budgetbill(session: Session, budgetbill_id: UUID7) -> BudgetBill:
    """Verify budget bill exists and return it.
    
    Args:
        session: Database session
        budgetbill_id: Budget bill identifier to verify
    
    Returns:
        BudgetBill object if found
    
    Raises:
        HTTPException: 404 if budget bill not found
    """
    budgetbill = session.get(BudgetBill, budgetbill_id)
    if not budgetbill:
        raise HTTPException(status_code=404, detail="Budget bill not found")
    return budgetbill


@router.get("/", response_model=list[Transactions])
def list_transactions(session: Session = Depends(get_session)):
    """Get all transactions.
    
    Args:
        session: Database session (injected)
    
    Returns:
        List of all transactions across all accounts and budget bills
    """
    return session.exec(select(Transactions)).all()


@router.get("/{transaction_id}", response_model=Transactions)
def get_transaction(transaction_id: UUID7, session: Session = Depends(get_session)):
    """Get a specific transaction by ID.
    
    Args:
        transaction_id: Unique transaction identifier (UUID7)
        session: Database session (injected)
    
    Returns:
        Transaction details
    
    Raises:
        HTTPException: 404 if transaction not found
    """
    transaction = session.get(Transactions, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.get("/account/{account_id}", response_model=list[Transactions])
def get_transactions_by_account(account_id: UUID7, session: Session = Depends(get_session)):
    """Get all transactions for a specific account.
    
    Args:
        account_id: Account identifier to filter transactions (UUID7)
        session: Database session (injected)
    
    Returns:
        List of transactions for the specified account
    
    Raises:
        HTTPException: 404 if account not found
    """
    _ensure_account(session, account_id)
    return session.exec(
        select(Transactions).where(Transactions.account_id == account_id)
    ).all()


@router.get("/budgetbill/{budgetbill_id}", response_model=list[Transactions])
def get_transactions_by_budgetbill(budgetbill_id: UUID7, session: Session = Depends(get_session)):
    """Get all transactions associated with a budget bill."""
    _ensure_budgetbill(session, budgetbill_id)
    return session.exec(select(Transactions).where(Transactions.budgetbill_id == budgetbill_id)).all()
