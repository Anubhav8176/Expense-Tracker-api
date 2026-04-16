from fastapi import FastAPI
from routers.router import router as auth_router
from db.session import Base, engine
from db.User import User
from db.Expense import Expense

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API")

app.include_router(auth_router, prefix="/auth", tags=["Auth"])