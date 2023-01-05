from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import Basket, create_async_session
from schemas import BasketSchema, BasketInDBSchema


class CRUDBasket(object):

    @staticmethod
    @create_async_session
    async def add(basket: BasketSchema, session: AsyncSession = None) -> BasketInDBSchema | None:
        baskets = Basket(
            **basket.dict()
        )
        session.add(baskets)
        try:
            await session.commit()
        except IntegrityError:
            pass
        else:
            await session.refresh(baskets)
            return BasketInDBSchema(**baskets.__dict__)

    @staticmethod
    @create_async_session
    async def delete(basket_id: int, session: AsyncSession = None) -> None:
        await session.execute(
            delete(Basket)
            .where(Basket.id == basket_id)
        )
        await session.commit()

    @staticmethod
    @create_async_session
    async def get(basket_id: int = None,
                  user_id: int = None,
                  product_id: int = None,
                  session: AsyncSession = None) -> BasketInDBSchema | None:
        if user_id:
            baskets = await session.execute(
                select(Basket)
                .where(Basket.user_id == user_id)
            )
        if product_id:
            baskets = await session.execute(
                select(Basket)
                .where(Basket.pizza_id == product_id)
            )
        else:
            baskets = await session.execute(
                select(Basket)
                .where(Basket.id == basket_id)
            )
        if basket := baskets.first():
            return BasketInDBSchema(**basket[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(user_id: int = None,
                      is_published: bool = None,
                      session: AsyncSession = None) -> list[BasketInDBSchema]:
        if user_id:
            baskets = await session.execute(
                select(Basket)
                .where(Basket.user_id == user_id)
            )
        elif is_published:
            baskets = await session.execute(
                select(Basket)
                .where(Basket.is_published == is_published)
            )
        else:
            baskets = await session.execute(
                select(Basket)
                .order_by(Basket.id)
            )
        return [BasketInDBSchema(**basket[0].__dict__) for basket in baskets]

    @staticmethod
    @create_async_session
    async def update(basket: BasketInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(Basket)
            .where(Basket.id == basket.id)
            .values(**basket.dict())
        )
        await session.commit()
