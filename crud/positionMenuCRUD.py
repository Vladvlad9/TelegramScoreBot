from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from models import PositionMenu, create_async_session
from schemas import PositionMenuInDBSchema


class CRUDPositionMenu(object):

    @staticmethod
    @create_async_session
    async def get(position_menu_id: int = None,
                  session: AsyncSession = None) -> PositionMenuInDBSchema | None:
        position_menus = await session.execute(
            select(PositionMenu)
            .where(PositionMenu.id == position_menu_id)
        )
        if position_menu := position_menus.first():
            return PositionMenuInDBSchema(**position_menu[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(session: AsyncSession = None) -> list[PositionMenuInDBSchema]:
        position_menus = await session.execute(
            select(PositionMenu)
            .order_by(PositionMenu.id)
        )
        return [PositionMenuInDBSchema(**position_menu[0].__dict__) for position_menu in position_menus]

    @staticmethod
    @create_async_session
    async def update(position_menu: PositionMenuInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(PositionMenu)
            .where(PositionMenu.id == position_menu.id)
            .values(**position_menu.dict())
        )
        await session.commit()
