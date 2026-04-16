from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from core.authentication import get_current_user
from db.session import get_db
from db.Expense import Expense
from schemas.models import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from typing import List

expense_router = APIRouter()


@expense_router.get("/", response_model=List[ExpenseResponse])
def get_all_expenses(
    page: int = 1,
    limit: int = 10,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    expenses = (
        db.query(Expense)
        .filter(Expense.user_id == current_user.id)
        .offset(limit * (page - 1))
        .limit(limit)
        .all()
    )
    return expenses


@expense_router.get("/{id}", response_model=ExpenseResponse)
def get_expense(
    id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    expense = db.query(Expense).filter(
        Expense.id == id,
        Expense.user_id == current_user.id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    return expense


@expense_router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_expense = Expense(
        **expense_data.model_dump(),
        user_id=current_user.id
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense


@expense_router.put("/{id}", response_model=ExpenseResponse)
def update_expense(
    id: str,
    expense_data: ExpenseUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    expense = db.query(Expense).filter(
        Expense.id == id,
        Expense.user_id == current_user.id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    for field, value in expense_data.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)

    return expense


@expense_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    id: str,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    expense = db.query(Expense).filter(
        Expense.id == id,
        Expense.user_id == current_user.id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()