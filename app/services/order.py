from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem


async def create_order(
    user_id: int,
    db: AsyncSession,
) -> Order:
    result = await db.execute(
        select(Cart)
        .options(
            selectinload(Cart.items).selectinload(CartItem.movie)
        )
        .where(Cart.user_id == user_id)
    )

    cart = result.scalar_one_or_none()

    if cart is None or not cart.items:
        raise ValueError("Cart is empty")

    total_amount = Decimal("0.00")

    order = Order(
        user_id=user_id,
        status=OrderStatus.PENDING,
        total_amount=Decimal("0.00"),
    )

    db.add(order)
    await db.flush()

    for cart_item in cart.items:
        price = cart_item.movie.price

        order_item = OrderItem(
            order_id=order.id,
            movie_id=cart_item.movie_id,
            price_at_order=price,
        )

        db.add(order_item)
        total_amount += price

    order.total_amount = total_amount

    for cart_item in cart.items:
        await db.delete(cart_item)

    await db.commit()

    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.movie)
        )
        .where(Order.id == order.id)
    )

    return result.scalar_one()
