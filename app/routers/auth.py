from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
)
from app.database import get_db
from app.models.user_group import UserGroup
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.services.auth import (
    activate_user,
    authenticate_user,
    register_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account with a hashed password.",
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserGroup).where(UserGroup.name == "user")
    )
    group = result.scalar_one_or_none()

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default user group does not exist",
        )

    try:
        user = await register_user(
            data=data,
            db=db,
            group_id=group.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return RegisterResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticates a user and returns access and refresh JWT tokens.",
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(
        email=data.email,
        password=data.password,
        db=db,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return LoginResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/activate/{token}",
    summary="Activate user account",
    description="Activates a user account using a valid activation token.",
)
async def activate(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await activate_user(
            token=token,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {
        "message": "User account activated successfully",
        "user_id": user.id,
    }
