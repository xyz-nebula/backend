from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")


class UserRegister(BaseModel):
    email: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4)
    timezone: str | None = Field(None, description="User's timezone in IANA format (e.g., 'America/New_York')")


__all__ = [
    "UserLogin", 
    "UserRegister",
]