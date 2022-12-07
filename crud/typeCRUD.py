from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, update, delete, and_

from models import Type, create_async_session
from schemas import TypeInDBSchema


class CRUDType(object):

    @staticmethod
    @create_async_session
    async def get(type_id: int = None,
                  session: AsyncSession = None) -> TypeInDBSchema | None:
        types = await session.execute(
            select(Type)
            .where(Type.id == type_id)
        )
        if typeF := types.first():
            return TypeInDBSchema(**typeF[0].__dict__)

    @staticmethod
    @create_async_session
    async def get_all(session: AsyncSession = None) -> list[TypeInDBSchema]:
        types = await session.execute(
            select(Type)
            .order_by(Type.id)
        )
        return [TypeInDBSchema(**typez[0].__dict__) for typez in types]

    @staticmethod
    @create_async_session
    async def update(types: TypeInDBSchema, session: AsyncSession = None) -> None:
        await session.execute(
            update(Type)
            .where(Type.id == types.id)
            .values(**types.dict())
        )
        await session.commit()
