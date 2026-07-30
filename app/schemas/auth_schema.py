from pydantic import BaseModel


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class RegisterResponse(BaseModel):
    message: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str

                   