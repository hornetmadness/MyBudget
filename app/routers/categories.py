"""Categories API Router

Provides RESTful API endpoints for bill category management including:
- CRUD operations for expense categories
- Soft delete support (deleted flag)
- Category filtering (active/deleted)
- Bill-to-category associations

Categories help organize and track spending by type (e.g., Utilities,
Groceries, Entertainment). Supports soft deletion to maintain
historical data integrity.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.models.database import Category, get_session
from app.models.schemas import CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[dict])
def list_categories(session: Session = Depends(get_session)):
    """List all active categories (excludes soft-deleted).
    
    Args:
        session: Database session (injected)
    
    Returns:
        List of category dictionaries with id, name, description, enabled,
        and timestamp fields
    """
    statement = select(Category).where(Category.deleted == False)
    categories = session.exec(statement).all()
    return [
        {
            "id": str(c.id),
            "name": c.name,
            "description": c.description,
            "enabled": c.enabled,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat(),
        }
        for c in categories
    ]


@router.get("/{category_id}", response_model=dict)
def get_category(category_id: UUID, session: Session = Depends(get_session)):
    """Get a specific category by ID.
    
    Args:
        category_id: Unique category identifier (UUID)
        session: Database session (injected)
    
    Returns:
        Category dictionary with all fields
    
    Raises:
        HTTPException: 404 if category not found or is soft-deleted
    """
    category = session.get(Category, str(category_id))
    if not category or category.deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return {
        "id": str(category.id),
        "name": category.name,
        "description": category.description,
        "enabled": category.enabled,
        "created_at": category.created_at.isoformat(),
        "updated_at": category.updated_at.isoformat(),
    }


@router.post("/", response_model=dict, status_code=201)
def create_category(category_data: CategoryCreate, session: Session = Depends(get_session)):
    """Create a new category.
    
    Args:
        category_data: Category creation data (name, description)
        session: Database session (injected)
    
    Returns:
        Created category dictionary with generated ID and timestamps
    
    Status:
        201: Category created successfully
    """
    """Create a new category."""
    # Check if category with this name already exists
    existing = session.exec(
        select(Category).where(Category.name == category_data.name, Category.deleted == False)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    category = Category(
        name=category_data.name,
        description=category_data.description,
    )
    session.add(category)
    session.commit()
    session.refresh(category)
    
    return {
        "id": str(category.id),
        "name": category.name,
        "description": category.description,
        "enabled": category.enabled,
        "created_at": category.created_at.isoformat(),
        "updated_at": category.updated_at.isoformat(),
    }


@router.patch("/{category_id}", response_model=dict)
def update_category(
    category_id: UUID, category_data: CategoryUpdate, session: Session = Depends(get_session)
):
    """Update a category."""
    category = session.get(Category, str(category_id))
    if not category or category.deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if new name conflicts with another category
    if category_data.name and category_data.name != category.name:
        existing = session.exec(
            select(Category).where(
                Category.name == category_data.name, 
                Category.deleted == False,
                Category.id != category.id
            )
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    update_data = category_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    
    session.add(category)
    session.commit()
    session.refresh(category)
    
    return {
        "id": str(category.id),
        "name": category.name,
        "description": category.description,
        "enabled": category.enabled,
        "created_at": category.created_at.isoformat(),
        "updated_at": category.updated_at.isoformat(),
    }


@router.delete("/{category_id}")
def delete_category(category_id: UUID, session: Session = Depends(get_session)):
    """Soft delete a category."""
    category = session.get(Category, str(category_id))
    if not category or category.deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    
    category.deleted = True
    session.add(category)
    session.commit()
    
    return {"message": "Category deleted"}
