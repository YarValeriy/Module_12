from pydantic import BaseModel, field_validator, Field, EmailStr
from datetime import date, datetime
from typing import Optional


# Pydantic models for request and response data validation

class ContactBase(BaseModel):
    name: str
    surname: str
    email: str
    phone: str
    birthday: date


class ContactCreate(ContactBase):
    name: str
    surname: str = None
    email: Optional[str] = None
    phone: str
    birthday: Optional[date]
    additional_data: Optional[str] = None

    @field_validator('email')
    def check_email(cls, v):
        if v == '':
            return None
        return v


class ContactUpdate(ContactCreate):
    pass


class ContactResponse(ContactCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


...


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
