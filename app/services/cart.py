from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.movie import Movie


async def add_movie_to_cart(
    user_id: int,
    movie_id: int,
    db: AsyncSession,
) -> CartItem:
    result = await db.execute(
        select(Movie).where(Movie.id == movie_id)
    )
    movie = result.scalar_one_or_none()

    if movie is None:
        raise ValueError("Movie not found")

    result = await db.execute(
        select(Cart).where(Cart.user_id == user_id)
    )
    cart = result.scalar_one_or_none()

    if cart is None:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.flush()

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.movie_id == movie_id,
        )
    )
    existing_item = result.scalar_one_or_none()

    if existing_item is not None:
        raise ValueError("Movie is already in cart")

    cart_item = CartItem(
        cart_id=cart.id,
        movie_id=movie_id,
    )

    db.add(cart_item)
    await db.commit()

    result = await db.execute(
        select(CartItem)
        .options(selectinload(CartItem.movie))
        .where(CartItem.id == cart_item.id)
    )

    return result.scalar_one()


async def remove_movie_from_cart(
    user_id: int,
    movie_id: int,
    db: AsyncSession,
) -> None:
    result = await db.execute(
        select(Cart).where(Cart.user_id == user_id)
    )
    cart = result.scalar_one_or_none()

    if cart is None:
        raise ValueError("Cart not found")

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.movie_id == movie_id,
        )
    )
    cart_item = result.scalar_one_or_none()

    if cart_item is None:
        raise ValueError("Movie is not in cart")

    await db.delete(cart_item)
    await db.commit()
