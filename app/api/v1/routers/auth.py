from fastapi import APIRouter, Depends, status

from app.api.v1.routers.models import (
    AuthActivationRequest,
    AuthLoginRequest,
    AuthLogoutRequest,
    AuthRefreshRequest,
    AuthRegisterRequest,
    AuthRegisterResponse,
    AuthTokens,
    TotpConfirmRequest,
    TotpDisableRequest,
    TotpEnrollResponse,
)
from app.dependencies import get_current_token_payload
from app.services.AuthService import AuthService, get_auth_service
from app.services.JWTService import TokenPayload

public_router = APIRouter(prefix="/auth", tags=["Authentication"])
protected_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    dependencies=[Depends(get_current_token_payload)],
)


@public_router.post("/register", response_model=AuthRegisterResponse)
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


@public_router.post("/register/activate", response_model=AuthTokens)
async def activate(
    body: AuthActivationRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthTokens:
    access_token, refresh_token = await auth_service.activate(str(body.code))
    return AuthTokens(access_token=access_token, refresh_token=refresh_token)


@public_router.post("/login", response_model=AuthTokens)
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


@public_router.post("/token/refresh", response_model=AuthTokens)
async def refresh(
    body: AuthRefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthTokens:
    access_token, refresh_token = await auth_service.refresh(body.refresh_token)
    return AuthTokens(access_token=access_token, refresh_token=refresh_token)


@protected_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: AuthLogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.logout(body.refresh_token)


@protected_router.post("/totp/enroll", response_model=TotpEnrollResponse)
async def enroll_totp(
    payload: TokenPayload = Depends(get_current_token_payload),
    auth_service: AuthService = Depends(get_auth_service),
) -> TotpEnrollResponse:
    secret, otpauth_url = await auth_service.enroll_totp(payload.sub)
    return TotpEnrollResponse(secret=secret, otpauth_url=otpauth_url)


@protected_router.post("/totp/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_totp(
    body: TotpConfirmRequest,
    payload: TokenPayload = Depends(get_current_token_payload),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.confirm_totp(payload.sub, body.totp_token)


@protected_router.delete("/totp", status_code=status.HTTP_204_NO_CONTENT)
async def disable_totp(
    body: TotpDisableRequest,
    payload: TokenPayload = Depends(get_current_token_payload),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.disable_totp(payload.sub, body.password)


router = APIRouter()
router.include_router(public_router)
router.include_router(protected_router)
