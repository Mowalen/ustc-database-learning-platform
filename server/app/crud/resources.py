from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.resource import Resource
from app.schemas.resources import ResourceCreate

async def create_resource(session: AsyncSession, resource: ResourceCreate) -> Resource:
    db_obj = Resource(
        filename=resource.filename,
        file_path=resource.file_path,
        url=resource.url,
        file_type=resource.file_type,
        size_bytes=resource.size_bytes,
        created_by=resource.created_by
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def get_resource(session: AsyncSession, resource_id: int) -> Resource | None:
    return await session.get(Resource, resource_id)
