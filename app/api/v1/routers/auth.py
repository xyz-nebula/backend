from fastapi import APIRouter, Depends, status

from app.api.v1.routers.models import (
    AuthActivationRequest,
    AuthLoginRequest,
    AuthLogoutRequest,
    AuthRefreshRequest,
    AuthRegisterRequest,
    AuthRegisterResponse,
    AuthTokens,
)
from app.dependencies import get_current_token_payload
from app.services.AuthService import AuthService, get_auth_service
from app.services.JWTService import TokenPayload

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/user/register", response_model=AuthRegisterResponse)
async def register(
    body: AuthRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthRegisterResponse:
    user = await auth_service.register(
        email=body.email,
        username=body.username,
        first_name=body.first_name,
        last_name=body.last_name,
        password=body.password,
    )
    return AuthRegisterResponse(user_id=user.uuid, status=user.status)


@router.post("/user/register/activate", response_model=AuthTokens)
async def activate(
    body: AuthActivationRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthTokens:
    access_token, refresh_token = await auth_service.activate(str(body.code))
    return AuthTokens(access_token=access_token, refresh_token=refresh_token)


@router.post("/user/login", response_model=AuthTokens)
async def login(
    body: AuthLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthTokens:
    access_token, refresh_token = await auth_service.login(
        email=body.email,
        password=body.password,
        totp_token=body.totp_token,
    )
    return AuthTokens(access_token=access_token, refresh_token=refresh_token)


@router.post("/token/refresh", response_model=AuthTokens)
async def refresh(
    body: AuthRefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthTokens:
    access_token, refresh_token = await auth_service.refresh(body.refresh_token)
    return AuthTokens(access_token=access_token, refresh_token=refresh_token)


@router.post("/user/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: AuthLogoutRequest,
    _: TokenPayload = Depends(get_current_token_payload),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.logout(body.refresh_token)
