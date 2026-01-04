from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.models.database import create_db_and_tables
from app.config import settings
from app.routers import (
    accounts,
    bills,
    transactions,
    budgets,
    settings as settings_router,
    categories,
    income,
    documentation,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown - add cleanup here if needed


app = FastAPI(title="MyBudget API", version=settings.APP_VERSION, lifespan=lifespan)

# Include routers
app.include_router(accounts.router)
app.include_router(bills.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(settings_router.router)
app.include_router(categories.router)
app.include_router(income.router)
app.include_router(documentation.router)


@app.get("/")
def root():
    """Welcome endpoint."""
    return {"message": "Welcome to MyBudget API"}
