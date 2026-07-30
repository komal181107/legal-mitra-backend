from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from app.models import User
from app.dependencies import get_current_user
from fastapi import APIRouter


from app.services.auth_service import AuthService

from app.schemas.auth_schema import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse
)


router = APIRouter()

auth_service = AuthService()


@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest):

    message = auth_service.register(
        name=request.name,
        email=request.email,
        password=request.password
    )

    return RegisterResponse(
        message=message
    )


@router.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    token = auth_service.login(
        email=form_data.username,
        password=form_data.password
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
    }