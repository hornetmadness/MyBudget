from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.database import AccountType, get_session

router = APIRouter(prefix="/account-types", tags=["account-types"])


@router.post("/", response_model=AccountType)
def create_account_type(account_type: AccountType, session: Session = Depends(get_session)):
    """Create a new account type."""
    session.add(account_type)
    session.commit()
    session.refresh(account_type)
    return account_type


@router.get("/", response_model=list[AccountType])
def list_account_types(session: Session = Depends(get_session)):
    """Get all account types."""
    account_types = session.exec(select(AccountType)).all()
    return account_types


@router.get("/{account_type_id}", response_model=AccountType)
def get_account_type(account_type_id: int, session: Session = Depends(get_session)):
    """Get a specific account type by ID."""
    account_type = session.get(AccountType, account_type_id)
    if not account_type:
        raise HTTPException(status_code=404, detail="Account type not found")
    return account_type


@router.patch("/{account_type_id}", response_model=AccountType)
def update_account_type(
    account_type_id: int,
    account_type_update: AccountType,
    session: Session = Depends(get_session),
):
    """Update an account type."""
    account_type = session.get(AccountType, account_type_id)
    if not account_type:
        raise HTTPException(status_code=404, detail="Account type not found")
    
    account_type_data = account_type_update.model_dump(exclude_unset=True)
    for key, value in account_type_data.items():
        setattr(account_type, key, value)
    
    session.add(account_type)
    session.commit()
    session.refresh(account_type)
    return account_type


@router.delete("/{account_type_id}")
def delete_account_type(account_type_id: int, session: Session = Depends(get_session)):
    """Delete an account type."""
    account_type = session.get(AccountType, account_type_id)
    if not account_type:
        raise HTTPException(status_code=404, detail="Account type not found")
    
    session.delete(account_type)
    session.commit()
    return {"ok": True}
