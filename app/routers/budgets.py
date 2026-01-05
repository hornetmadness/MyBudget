"""Budgets API Router

Provides RESTful API endpoints for budget management including:
- Budget CRUD operations with date validation
- Budget bill associations (linking bills to budgets)
- Payment tracking and status updates
- Budget overlap validation
- Spending analysis

Budgets represent time-based spending plans with associated bills.
The system prevents overlapping budget periods. All dates are stored
in UTC internally and converted to app timezone for display.
"""

from datetime import timedelta, timezone, datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from uuid import UUID
from app.models.database import Budget, BudgetBill, Account, Bill, Transactions, ApplicationSettings, get_session
from app.models.schemas import BudgetCreate, BudgetUpdate, BudgetBillCreate, BudgetBillUpdate
from app.utils import utc_now, to_utc, ensure_aware_utc

# Type alias for UUID7
UUID7 = UUID

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("/", response_model=Budget)
def create_budget(budget: BudgetCreate, session: Session = Depends(get_session)):
    """Create a new budget with overlap validation.
    
    Validates that the new budget period does not overlap with any existing
    budget periods. All dates are normalized to UTC for storage.
    
    Args:
        budget: Budget creation data (name, start_date, end_date)
        session: Database session (injected)
    
    Returns:
        Created budget with generated ID
    
    Raises:
        HTTPException: 400 if budget overlaps with existing budget
    """
    # Normalize new budget dates to UTC for storage (ensure aware)
    new_start = ensure_aware_utc(to_utc(budget.start_date))
    new_end = ensure_aware_utc(to_utc(budget.end_date))
    new_start_ts = new_start.timestamp()
    new_end_ts = new_end.timestamp()
    
    # Check for overlapping budgets
    # A budget overlaps if it starts before another ends AND ends after another starts
    existing_budgets = session.exec(select(Budget)).all()
    
    for existing in existing_budgets:
        existing_start = ensure_aware_utc(existing.start_date)
        existing_end = ensure_aware_utc(existing.end_date)

        if not existing_start or not existing_end:
            continue

        es_ts = existing_start.timestamp()
        ee_ts = existing_end.timestamp()

        # Check if new budget overlaps with existing budget using UTC timestamps
        # Overlap occurs if: new_start < existing_end AND new_end > existing_start
        if new_start_ts < ee_ts and new_end_ts > es_ts:
            raise HTTPException(
                status_code=400,
                detail=f"Budget overlaps with existing budget '{existing.name}' (from {existing.start_date.date()} to {existing.end_date.date()})"
            )
    
    db_budget = Budget.model_validate(budget)
    db_budget.start_date = new_start
    db_budget.end_date = new_end
    session.add(db_budget)
    session.commit()
    session.refresh(db_budget)
    return db_budget


@router.get("/", response_model=list[Budget])
def list_budgets(session: Session = Depends(get_session)):
    """Get all budgets."""
    budgets = session.exec(select(Budget)).all()
    return budgets


@router.get("/{budget_id}", response_model=Budget)
def get_budget(budget_id: UUID7, session: Session = Depends(get_session)):
    """Get a specific budget by ID."""
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.patch("/{budget_id}", response_model=Budget)
def update_budget(
    budget_id: UUID7,
    budget_update: BudgetUpdate,
    session: Session = Depends(get_session),
):
    """Update a budget. Validates no overlap with other existing budgets."""
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # If dates are being updated, check for overlaps with other budgets
    if budget_update.start_date or budget_update.end_date:
        new_start_date = ensure_aware_utc(to_utc(budget_update.start_date) if budget_update.start_date else budget.start_date)
        new_end_date = ensure_aware_utc(to_utc(budget_update.end_date) if budget_update.end_date else budget.end_date)
        new_start_ts = new_start_date.timestamp()
        new_end_ts = new_end_date.timestamp()
        
        # Check for overlapping budgets (excluding the current one)
        existing_budgets = session.exec(select(Budget).where(Budget.id != budget_id)).all()
        
        for existing in existing_budgets:
            existing_start = ensure_aware_utc(existing.start_date)
            existing_end = ensure_aware_utc(existing.end_date)

            if not existing_start or not existing_end:
                continue

            es_ts = existing_start.timestamp()
            ee_ts = existing_end.timestamp()

            # Check if updated budget would overlap with existing budget (UTC timestamps)
            if new_start_ts < ee_ts and new_end_ts > es_ts:
                raise HTTPException(
                    status_code=400,
                    detail=f"Budget would overlap with existing budget '{existing.name}' (from {existing.start_date.date()} to {existing.end_date.date()})"
                )
    
    budget_data = budget_update.model_dump(exclude_unset=True)
    # Convert dates to UTC if provided
    if "start_date" in budget_data and budget_data["start_date"]:
        budget_data["start_date"] = to_utc(budget_data["start_date"])
    if "end_date" in budget_data and budget_data["end_date"]:
        budget_data["end_date"] = to_utc(budget_data["end_date"])
    
    for key, value in budget_data.items():
        setattr(budget, key, value)
    
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return budget


@router.delete("/{budget_id}")
def delete_budget(budget_id: UUID7, session: Session = Depends(get_session)):
    """Delete a budget."""
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    # Prevent deletion when bills are attached
    has_bills = session.exec(
        select(BudgetBill.id).where(BudgetBill.budget_id == budget_id)
    ).first()
    if has_bills is not None:
        raise HTTPException(status_code=400, detail="Budget has bills and cannot be deleted")
    
    session.delete(budget)
    session.commit()
    return {"ok": True}


# Budget-Bill association endpoints
@router.post("/{budget_id}/bills", response_model=BudgetBill)
def add_bill_to_budget(
    budget_id: UUID7,
    budget_bill: BudgetBillCreate,
    session: Session = Depends(get_session),
):
    """Add a bill to a budget with a specific budgeted amount."""
    # Verify budget exists
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Verify bill exists
    bill = session.get(Bill, budget_bill.bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    # Verify account exists
    account = session.get(Account, budget_bill.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Validate bill occurrence fits within budget window
    # Skip validation for "always" frequency bills - they apply to any budget
    # Also skip if an explicit due_date is provided that falls within budget
    budget_start = budget.start_date
    budget_end = budget.end_date
    
    # Normalize budget dates to be timezone-aware
    if budget_start and budget_start.tzinfo is None:
        budget_start = budget_start.replace(tzinfo=timezone.utc)
    if budget_end and budget_end.tzinfo is None:
        budget_end = budget_end.replace(tzinfo=timezone.utc)
    
    # If due_date is explicitly provided, validate it falls within budget
    if budget_bill.due_date:
        due_date_val = budget_bill.due_date
        if due_date_val.tzinfo is None:
            due_date_val = due_date_val.replace(tzinfo=timezone.utc)
        
        if not (budget_start <= due_date_val <= budget_end):
            raise HTTPException(
                status_code=400,
                detail=f"Due date {due_date_val.date()} is outside budget window ({budget_start.date()} to {budget_end.date()})",
            )
    else:
        # Use bill's start_freq if available, otherwise default to budget's start_date for recurrence validation
        bill_start = bill.start_freq if bill.start_freq else budget_start
        
        # Normalize bill_start to be timezone-aware
        if bill_start and bill_start.tzinfo is None:
            bill_start = bill_start.replace(tzinfo=timezone.utc)
        
        bill_freq = (bill.frequency or "monthly").lower() if hasattr(bill, "frequency") else "monthly"

        def add_months(dt, months: int):
            m = dt.month - 1 + months
            y = dt.year + m // 12
            m = m % 12 + 1
            # Clamp day to last day of target month
            days_in_month = [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
            d = min(dt.day, days_in_month)
            return dt.replace(year=y, month=m, day=d)

        def next_occurrence(dt, freq: str):
            if freq == "always":
                return None  # Always bills don't need date range validation
            if freq == "once":
                return None  # One-time bills don't recur
            if freq == "daily":
                return dt + timedelta(days=1)
            if freq == "weekly":
                return dt + timedelta(days=7)
            if freq == "biweekly":
                return dt + timedelta(days=14)
            if freq == "semimonthly":
                # Custom logic for semimonthly (twice per month) if needed
                return add_months(dt, 1)  # Placeholder: adjust as needed
            if freq == "monthly":
                return add_months(dt, 1)
            if freq == "yearly":
                return add_months(dt, 12)
            return dt + timedelta(days=365)

        # Only validate date range for recurring bills, not for "always" bills
        calculated_due_date = None
        if bill_freq != "always" and budget_start and budget_end and bill_start:
            current = bill_start
            fits = False
            for _ in range(100):  # avoid infinite loops
                if budget_start <= current <= budget_end:
                    fits = True
                    calculated_due_date = current
                    break
                if current > budget_end:
                    break
                next_occ = next_occurrence(current, bill_freq)
                if next_occ is None:  # One-time bill or always bill
                    break
                current = next_occ
            if not fits:
                bill_name = bill.name if hasattr(bill, "name") else "Bill"
                raise HTTPException(
                    status_code=400,
                    detail=f"Bill '{bill_name}' does not occur within budget date window",
                )
    
    # Use bill's budgeted_amount when not provided
    budget_bill_data = budget_bill.model_dump()
    if budget_bill_data.get("budgeted_amount") is None:
        budget_bill_data["budgeted_amount"] = bill.budgeted_amount
    
    # Use bill's transfer_account_id when not provided
    if budget_bill_data.get("transfer_account_id") is None:
        budget_bill_data["transfer_account_id"] = bill.transfer_account_id
    
    # Set the due_date - use provided due_date or calculated one
    if budget_bill.due_date:
        # Already has due_date from request, don't override
        pass
    elif 'calculated_due_date' in locals() and calculated_due_date is not None:
        budget_bill_data["due_date"] = calculated_due_date
    elif bill.frequency and bill.frequency.lower() == "always":
        budget_bill_data["due_date"] = datetime.now(timezone.utc)

    # Create budget-bill association
    db_budget_bill = BudgetBill.model_validate(
        budget_bill_data, update={"budget_id": budget_id}
    )
    session.add(db_budget_bill)
    session.commit()
    session.refresh(db_budget_bill)
    return db_budget_bill


@router.get("/{budget_id}/bills", response_model=list[BudgetBill])
def get_budget_bills(budget_id: UUID7, session: Session = Depends(get_session)):
    """Get all bills associated with a budget."""
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    budget_bills = session.exec(
        select(BudgetBill).where(BudgetBill.budget_id == budget_id)
    ).all()
    return budget_bills


@router.patch("/{budget_id}/bills/{budget_bill_id}", response_model=BudgetBill)
def update_budget_bill(
    budget_id: UUID7,
    budget_bill_id: UUID7,
    budget_bill_update: BudgetBillUpdate,
    session: Session = Depends(get_session),
):
    """Update a budget-bill association."""
    budget_bill = session.get(BudgetBill, budget_bill_id)
    if not budget_bill or budget_bill.budget_id != budget_id:
        raise HTTPException(status_code=404, detail="Budget bill not found")
    
    budget_bill_data = budget_bill_update.model_dump(exclude_unset=True)
    
    # Normalize/auto-set paid_on
    if "paid_amount" in budget_bill_data and budget_bill_data["paid_amount"] is not None:
        paid_amt = budget_bill_data["paid_amount"]
        if paid_amt > 0:
            from datetime import datetime, timezone, time
            # If caller didn't supply paid_on, default to now (UTC)
            if "paid_on" not in budget_bill_data:
                budget_bill_data["paid_on"] = utc_now()
            else:
                paid_on_val = budget_bill_data["paid_on"]
                # If tz-naive, assume UTC
                if paid_on_val.tzinfo is None:
                    paid_on_val = paid_on_val.replace(tzinfo=timezone.utc)
                # If time component is midnight (likely date-only input), set to current UTC time on same date
                if (
                    paid_on_val.hour == 0
                    and paid_on_val.minute == 0
                    and paid_on_val.second == 0
                    and paid_on_val.microsecond == 0
                ):
                    now_utc = utc_now()
                    paid_on_val = datetime.combine(paid_on_val.date(), now_utc.time(), tzinfo=timezone.utc)
                budget_bill_data["paid_on"] = paid_on_val
    
    # Check if marking as paid (paid_on and paid_amount are being set)
    is_marking_paid = (
        "paid_on" in budget_bill_data 
        and budget_bill_data["paid_on"] is not None
        and "paid_amount" in budget_bill_data
        and budget_bill_data["paid_amount"] is not None
        and budget_bill_data["paid_amount"] > 0
    )
    
    # If marking as paid, verify account is enabled
    if is_marking_paid:
        account = session.get(Account, budget_bill.account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        if not account.enabled:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot pay bill using disabled account '{account.name}'"
            )
    
    for key, value in budget_bill_data.items():
        setattr(budget_bill, key, value)
    
    session.add(budget_bill)
    session.commit()
    session.refresh(budget_bill)
    
    # Create transaction if marking as paid
    if is_marking_paid:
        budget = session.get(Budget, budget_id)
        # Use the budget-bill note if present; otherwise use a generic fallback with budget name.
        note = budget_bill.note or f"Payment for bill via budget {budget.name}"

        transaction = Transactions(
            account_id=budget_bill.account_id,
            budgetbill_id=budget_bill.id,
            amount=budget_bill.paid_amount,
            transaction_type="debit",
            note=note,
        )
        session.add(transaction)
        session.commit()
        
        # Update account balance
        account = session.get(Account, budget_bill.account_id)
        if account:
            account.balance -= budget_bill.paid_amount
            session.add(account)
            session.commit()
        
        # If this is a transfer, create a credit transaction to the transfer account
        if budget_bill.transfer_account_id:
            transfer_account = session.get(Account, budget_bill.transfer_account_id)
            if transfer_account:
                transfer_account.balance += budget_bill.paid_amount
                session.add(transfer_account)
                session.commit()
                
                # Create credit transaction for the transfer account
                transfer_note = f"Transfer from {account.name if account else 'unknown'}: {note}" if account else note
                transfer_transaction = Transactions(
                    account_id=budget_bill.transfer_account_id,
                    budgetbill_id=budget_bill.id,
                    amount=budget_bill.paid_amount,
                    transaction_type="credit",
                    note=transfer_note,
                )
                session.add(transfer_transaction)
                session.commit()
    
    return budget_bill


@router.delete("/{budget_id}/bills/{budget_bill_id}")
def remove_bill_from_budget(
    budget_id: UUID7,
    budget_bill_id: UUID7,
    session: Session = Depends(get_session),
):
    """Remove a bill from a budget."""
    budget_bill = session.get(BudgetBill, budget_bill_id)
    if not budget_bill or budget_bill.budget_id != budget_id:
        raise HTTPException(status_code=404, detail="Budget bill not found")
    
    session.delete(budget_bill)
    session.commit()
    return {"ok": True}

@router.get("/prune/list")
def list_budgets_to_prune(session: Session = Depends(get_session)):
    """List budgets that would be pruned based on prune_budgets_after_months setting."""
    # Get the setting
    setting = session.exec(
        select(ApplicationSettings).where(ApplicationSettings.key == "prune_budgets_after_months")
    ).first()
    
    months_to_keep = int(setting.value) if setting else 24
    
    # Calculate cutoff date
    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=months_to_keep * 30)  # Approximate month as 30 days
    
    # Find budgets with end_date before cutoff
    old_budgets = session.exec(
        select(Budget).where(Budget.end_date < cutoff_date, Budget.deleted == False)
    ).all()
    
    return [
        {
            "id": str(b.id),
            "name": b.name,
            "end_date": b.end_date.isoformat() if b.end_date else None,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }
        for b in old_budgets
    ]


@router.post("/prune")
def prune_old_budgets(session: Session = Depends(get_session)):
    """Soft delete budgets older than prune_budgets_after_months setting."""
    # Get the setting
    setting = session.exec(
        select(ApplicationSettings).where(ApplicationSettings.key == "prune_budgets_after_months")
    ).first()
    
    months_to_keep = int(setting.value) if setting else 24
    
    # Calculate cutoff date
    now = datetime.now(timezone.utc)
    cutoff_date = now - timedelta(days=months_to_keep * 30)  # Approximate month as 30 days
    
    # Find and soft delete budgets with end_date before cutoff
    old_budgets = session.exec(
        select(Budget).where(Budget.end_date < cutoff_date, Budget.deleted == False)
    ).all()
    
    count = 0
    for budget in old_budgets:
        budget.deleted = True
        session.add(budget)
        count += 1
    
    session.commit()
    
    return {
        "message": f"Pruned {count} budgets",
        "count": count,
        "cutoff_date": cutoff_date.isoformat(),
        "months_retained": months_to_keep,
    }