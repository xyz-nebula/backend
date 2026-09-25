from fastapi import APIRouter, Depends, status

from app.dependencies import get_current_token_payload


admin_router = APIRouter(
    prefix="/admins", tags=["Admin"], dependencies=[Depends(get_current_token_payload)]
)


@admin_router.get("/",)
async def get_admins():...


@admin_router.post("/",)
async def set_admin():
    """
    Sets your user as an admin if the code is provided in the environment variable ADMIN_CODE
    """
    ...