from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import PizzaMenu, create_async_session
from schemas import PizzaMenuSchemaInDBSchema, PizzaMenuSchema


class CRUDPizzaMenu(object):

    @staticmethod
    @create_async_session
    async def add(pizzaMenu: PizzaMenuSchema, session: AsyncSession = None) -> PizzaMenuSchemaInDBSchema | None:
        pizzas = PizzaMenu(
            **pizzaMenu.dict()
        )
        session.add(pizzas)
        try:
            await session.commit()
        except IntegrityError:
            pass
        else:
            await session.refresh(pizzas)
            return PizzaMenuSchemaInDBSchema(**pizzas.__dict__)

    @staticmethod
    @create_async_session
    async def delete(pizzaMenu_id: int, session: AsyncSession = None) -> None:
        await session.execute(
            delete(PizzaMenu)
            .where(PizzaMenu.id == pizzaMenu_id)
        )
        await session.commit()

    @staticmethod
    @create_async_session
    async def get(pizzaMenu_id: int = None,
                  session: AsyncSession = None) -> PizzaMenuSchemaInDBSchema | None:
        pizzas = await session.execute(
            select(PizzaMenu)
            .where(PizzaMenu.id == pizzaMenu_id)
        )
        if pizzas_menu := pizzas.first():
            return PizzaMenuSchemaInDBSchema(**pizzas_menu[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(session: AsyncSession = None) -> list[PizzaMenuSchemaInDBSchema]:
        pizzas = await session.execute(
            select(PizzaMenu)
            .order_by(PizzaMenu.id)
        )
        return [PizzaMenuSchemaInDBSchema(**pizzaMenu[0].__dict__) for pizzaMenu in pizzas]

    @staticmethod
    @create_async_session
    async def update(pizzaMenu: PizzaMenuSchemaInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(PizzaMenu)
            .where(PizzaMenu.id == pizzaMenu.id)
            .values(**pizzaMenu.dict())
        )
        await session.commit()
