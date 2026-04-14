from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = ""
    password: str = ""


class ProfileUpdateRequest(BaseModel):
    full_name: str
    username: str
    email: str = ""
    new_password: str = ""


class IncomePayload(BaseModel):
    income_date: date
    amount: float = Field(gt=0)
    source: str
    description: str


class ExpensePayload(BaseModel):
    expense_date: date
    amount: float = Field(gt=0)
    name: str
    category: str
    description: str
    paid_by: str
    expense_type: str
    split_type: str = "equal"
    split_ratio: float = 0.5


class SettledPayload(BaseModel):
    is_settled: bool


class CategoryPayload(BaseModel):
    name: str

