from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactModel(BaseModel):
    """
    Schema for contact creation.
    """

    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone: str = Field(max_length=20)
    birthday: date
    additional_data: str | None = Field(default=None, max_length=250)


class ContactUpdate(ContactModel):
    """
    Schema for updating contact information.
    """

    pass


class ContactResponse(ContactModel):
    """
    Schema for contact response.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Schema for user registration.
    """

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class UserResponse(BaseModel):
    """
    Schema for user response.
    """

    id: int
    username: str
    email: EmailStr
    avatar: str | None = None
    confirmed: bool
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """
    Schema for JWT authentication token.
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Schema for email verification request.
    """

    email: EmailStr


class RequestPasswordReset(BaseModel):
    """
    Schema for password reset request.
    """

    email: EmailStr


class ResetPassword(BaseModel):
    """Schema for resetting user password."""

    password: str = Field(min_length=6, max_length=72)
