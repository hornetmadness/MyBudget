from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from datetime import datetime, timezone
from pathlib import Path
import os
from app.models.database import ApplicationSettings, get_session
from app.models.schemas import SettingsCreate, SettingsUpdate
from typing import Dict, Any

router = APIRouter(prefix="/settings", tags=["settings"])

# Default settings
DEFAULT_SETTINGS = {
    "currency_symbol": "$",
    "decimal_places": "2",
    "number_format": "comma",
    "prune_budgets_after_months": "24",
}


def _get_or_create_setting(session: Session, key: str, default_value: str) -> ApplicationSettings:
    """Get a setting by key, creating it with default value if it doesn't exist."""
    setting = session.exec(select(ApplicationSettings).where(ApplicationSettings.key == key)).first()
    
    if not setting:
        setting = ApplicationSettings(key=key, value=default_value)
        session.add(setting)
        session.commit()
        session.refresh(setting)
    
    return setting


def _get_all_settings(session: Session) -> Dict[str, Any]:
    """Get all settings as a dictionary, creating defaults if needed."""
    settings = {}
    
    for key, default_value in DEFAULT_SETTINGS.items():
        setting = _get_or_create_setting(session, key, default_value)
        # Convert values back to appropriate types
        if key in ("decimal_places", "prune_budgets_after_months"):
            settings[key] = int(setting.value)
        else:
            settings[key] = setting.value
    
    return settings


@router.get("/")
def get_settings(session: Session = Depends(get_session)):
    """Get all application settings as a dictionary. Creates default settings if they don't exist."""
    return _get_all_settings(session)


@router.post("/")
def create_settings(settings_data: SettingsCreate, session: Session = Depends(get_session)):
    """Create/replace all application settings."""
    # Delete existing settings
    existing = session.exec(select(ApplicationSettings)).all()
    for setting in existing:
        session.delete(setting)
    session.commit()
    
    # Create new settings from the provided data
    data_dict = settings_data.model_dump(exclude_unset=True)
    for key, value in data_dict.items():
        new_setting = ApplicationSettings(key=key, value=str(value))
        session.add(new_setting)
    
    session.commit()
    return _get_all_settings(session)


@router.patch("/")
def update_settings(
    settings_update: SettingsUpdate,
    session: Session = Depends(get_session),
):
    """Update individual application settings."""
    update_data = settings_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setting = session.exec(select(ApplicationSettings).where(ApplicationSettings.key == key)).first()
        
        if setting:
            setting.value = str(value)
            setting.updated_at = datetime.now(timezone.utc)
            session.add(setting)
        else:
            # Create new setting if it doesn't exist
            new_setting = ApplicationSettings(key=key, value=str(value))
            session.add(new_setting)
    
    session.commit()
    return _get_all_settings(session)


@router.get("/backup/download-db")
def download_database():
    """Download the application database file."""
    # Get the database file path from environment or use default
    db_url = os.getenv("DATABASE_URL", "sqlite:///./mybudget.db")
    
    # Extract the file path from the database URL
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    else:
        raise HTTPException(status_code=400, detail="Only SQLite databases can be backed up")
    
    # Convert to absolute path if relative
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.getcwd(), db_path)
    
    # Check if file exists
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Database file not found")
    
    # Return the file
    return FileResponse(
        path=db_path,
        filename=f"mybudget_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.db",
        media_type="application/octet-stream"
    )
