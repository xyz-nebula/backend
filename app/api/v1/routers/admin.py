from fastapi import APIRouter, Depends, status

from app.api.v1.routers.models import AdminRegisterRequest
from app.dependencies import TokenPayload, get_current_token_payload
from app.services.AdminService import AdminService, get_admin_service
from app.services.AuthService import AuthService, get_auth_service

admin_router = APIRouter(
    prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_token_payload)]
)

case_router = APIRouter(
    prefix="/cases", tags=["Cases"], dependencies=[Depends(get_current_token_payload)]
)


@admin_router.get("/",)
async def get_admins():...



@admin_router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def set_admin(
    body: AdminRegisterRequest,
    payload: TokenPayload = Depends(get_current_token_payload),
    admin_service: AdminService = Depends(get_admin_service),
    user_service: AuthService = Depends(get_auth_service),
):
    """
    Sets your user as an admin if the code is provided in the environment variable ADMIN_CODE
    """
    user = await user_service._require_user(payload.sub)
    _ = await admin_service.set_user_admin(user, code=body.code)

    return {"message": "User role set to admin successfully"}


router = APIRouter()
router.include_router(admin_router)
router.include_router(case_router)