from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import Menu, create_async_session
from schemas import PizzaMenuSchemaInDBSchema, PizzaMenuSchema


class CRUDPizzaMenu(object):

    @staticmethod
    @create_async_session
    async def add(pizzaMenu: PizzaMenuSchema, session: AsyncSession = None) -> PizzaMenuSchemaInDBSchema | None:
        pizzas = Menu(
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
            delete(Menu)
            .where(Menu.id == pizzaMenu_id)
        )
        await session.commit()

    @staticmethod
    @create_async_session
    async def get(menu_id: int,
                  parent_id: int,
                  session: AsyncSession = None) -> PizzaMenuSchemaInDBSchema | None:
        pizzas = await session.execute(
            select(Menu)
            .where(Menu.id == menu_id, and_(Menu.parent_id == parent_id))
        )
        if pizzas_menu := pizzas.first():
            return PizzaMenuSchemaInDBSchema(**pizzas_menu[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(position_id: int = None,
                      session: AsyncSession = None) -> list[PizzaMenuSchemaInDBSchema]:
        if position_id:
            pizzas = await session.execute(
                select(Menu)
                .where(Menu.parent_id == position_id)
            )
        else:
            pizzas = await session.execute(
                select(Menu)
                .order_by(Menu.id)
            )
        return [PizzaMenuSchemaInDBSchema(**pizzaMenu[0].__dict__) for pizzaMenu in pizzas]

    @staticmethod
    @create_async_session
    async def update(pizzaMenu: PizzaMenuSchemaInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(Menu)
            .where(Menu.id == pizzaMenu.id)
            .values(**pizzaMenu.dict())
        )
        await session.commit()
