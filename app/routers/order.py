from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.order import OrderResponse, OrderItemResponse
from app.services.order import create_order, get_user_orders


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create order",
    description="Creates an order from the current user's shopping cart.",
)
async def create_user_order(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        order = await create_order(
            user_id=current_user.id,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return OrderResponse(
        id=order.id,
        created_at=order.created_at,
        status=order.status,
        total_amount=order.total_amount,
        items=[
            OrderItemResponse(
                id=item.id,
                movie_id=item.movie_id,
                movie_name=item.movie.name,
                price_at_order=item.price_at_order,
            )
            for item in order.items
        ],
    )


@router.get(
    "",
    response_model=list[OrderResponse],
    summary="Get current user's orders",
    description="Returns all orders belonging to the current user.",
)
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    orders = await get_user_orders(
        user_id=current_user.id,
        db=db,
    )

    return [
        OrderResponse(
            id=order.id,
            created_at=order.created_at,
            status=order.status,
            total_amount=order.total_amount,
            items=[
                OrderItemResponse(
                    id=item.id,
                    movie_id=item.movie_id,
                    movie_name=item.movie.name,
                    price_at_order=item.price_at_order,
                )
                for item in order.items
            ],
        )
        for order in orders
    ]
