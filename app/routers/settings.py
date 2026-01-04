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

# Default settings - each entry: {key: (value, display_name)}
DEFAULT_SETTINGS = {
    "currency_symbol": ("$", "Currency Symbol"),
    "decimal_places": ("2", "Decimal Places"),
    "number_format": ("comma", "Number Format"),
    "prune_budgets_after_months": ("24", "Prune Budgets After (months)"),
    "show_num_old_budgets": ("3", "Show Number of Old Budgets"),
    "timezone": ("America/New_York", "Timezone"),
}


def _get_or_create_setting(session: Session, key: str, default_value: str, display_name: str) -> ApplicationSettings:
    """Get a setting by key, creating it with default value if it doesn't exist."""
    setting = session.exec(select(ApplicationSettings).where(ApplicationSettings.key == key)).first()
    
    if not setting:
        setting = ApplicationSettings(key=key, value=default_value, display_name=display_name)
        session.add(setting)
        session.commit()
        session.refresh(setting)
    
    return setting


def _get_all_settings(session: Session) -> Dict[str, Any]:
    """Get all settings as a dictionary, creating defaults if needed."""
    settings = {}
    
    for key, (default_value, display_name) in DEFAULT_SETTINGS.items():
        setting = _get_or_create_setting(session, key, default_value, display_name)
        # Convert values back to appropriate types
        if key in ("decimal_places", "prune_budgets_after_months", "show_num_old_budgets"):
            settings[key] = {"value": int(setting.value), "display_name": setting.display_name}
        else:
            settings[key] = {"value": setting.value, "display_name": setting.display_name}
    
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
        # Get display_name from defaults if available
        display_name = DEFAULT_SETTINGS.get(key, ("", key))[1]
        new_setting = ApplicationSettings(key=key, value=str(value), display_name=display_name)
        session.add(new_setting)
    
    session.commit()
    return _get_all_settings(session)


@router.patch("/")
def update_settings(
    settings_update: SettingsUpdate,
    session: Session = Depends(get_session),
):
    """Update individual application settings."""
    data_dict = settings_update.model_dump(exclude_unset=True)
    
    for key, value in data_dict.items():
        setting = session.exec(
            select(ApplicationSettings).where(ApplicationSettings.key == key)
        ).first()
        
        if setting:
            setting.value = str(value)
        else:
            # Get display_name from defaults if available
            display_name = DEFAULT_SETTINGS.get(key, ("", key))[1]
            setting = ApplicationSettings(key=key, value=str(value), display_name=display_name)
            session.add(setting)
    
    session.commit()
    return _get_all_settings(session)


@router.get("/database")
def download_database(session: Session = Depends(get_session)):
    """Download the database file."""
    db_path = Path(os.getenv("DATABASE_PATH", "budget.db"))
    
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Database file not found")
    
    # Create a timestamped filename
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"budget_backup_{timestamp}.db"
    
    return FileResponse(
        path=str(db_path),
        filename=filename,
        media_type="application/octet-stream"
    )
