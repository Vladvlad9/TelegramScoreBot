from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import Basket, create_async_session
from schemas import BasketInDBSchema, BasketSchema


class CRUDBasket(object):

    @staticmethod
    @create_async_session
    async def add(basket: BasketSchema, session: AsyncSession = None) -> BasketInDBSchema | None:
        baskets = BasketSchema(
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
    async def get(basket_id: int = None,
                  session: AsyncSession = None) -> BasketInDBSchema | None:
        baskets = await session.execute(
            select(Basket)
            .where(Basket.id == basket_id)
        )
        if basket := baskets.first():
            return BasketInDBSchema(**basket[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(session: AsyncSession = None) -> list[BasketInDBSchema]:
        baskets = await session.execute(
            select(Basket)
            .order_by(Basket.id)
        )
        return [BasketInDBSchema(**basket[0].__dict__) for basket in baskets]

    @staticmethod
    @create_async_session
    async def update(baskets: BasketInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(Basket)
            .where(Basket.id == baskets.id)
            .values(**baskets.dict())
        )
        await session.commit()
