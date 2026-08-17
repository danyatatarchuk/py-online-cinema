from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.cart import CartItemResponse, CartResponse
from app.services.cart import (
    add_movie_to_cart,
    remove_movie_from_cart,
    get_cart,
)


router = APIRouter(
    prefix="/cart",
    tags=["Shopping Cart"],
)


@router.post(
    "/items/{movie_id}",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add movie to cart",
    description="Adds a movie to the current user's shopping cart.",
)
async def add_to_cart(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        cart_item = await add_movie_to_cart(
            user_id=current_user.id,
            movie_id=movie_id,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return CartItemResponse(
        id=cart_item.id,
        movie_id=cart_item.movie_id,
        movie_name=cart_item.movie.name,
        price=cart_item.movie.price,
    )


@router.delete(
    "/items/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove movie from cart",
    description="Removes a movie from the current user's shopping cart.",
)
async def remove_from_cart(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await remove_movie_from_cart(
            user_id=current_user.id,
            movie_id=movie_id,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=CartResponse,
    summary="View cart",
    description="Returns the current user's shopping cart.",
)
async def view_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        cart = await get_cart(
            user_id=current_user.id,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return CartResponse(
        items=[
            CartItemResponse(
                id=item.id,
                movie_id=item.movie_id,
                movie_name=item.movie.name,
                price=item.movie.price,
            )
            for item in cart.items
        ]
    )
