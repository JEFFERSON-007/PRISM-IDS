"""Concrete Generic Base Service Implementation."""

from typing import Generic, Optional, TypeVar, Sequence, Any
from pydantic import BaseModel
from app.database.base import Base
from app.domain.interfaces.repository import IRepository
from app.domain.interfaces.service import IService
from app.core.exceptions import NotFoundError

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(
    IService[ModelType, CreateSchemaType, UpdateSchemaType],
    Generic[ModelType, CreateSchemaType, UpdateSchemaType],
):
    """Generic Base Service wrapping repository calls with business validation."""

    def __init__(self, repository: IRepository[ModelType]) -> None:
        self.repository = repository

    async def get(self, id: Any) -> Optional[ModelType]:
        """Fetch single entity by ID."""
        entity = await self.repository.get_by_id(id)
        if not entity:
            raise NotFoundError(message=f"Entity with ID '{id}' not found.")
        return entity

    async def get_multi(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Fetch paginated entities."""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Instantiate and persist entity from creation schema."""
        entity_dict = obj_in.model_dump()
        # Subclasses can override or extend this instantiation logic
        raise NotImplementedError("Subclasses must implement entity construction from schema")

    async def update(self, id: Any, obj_in: UpdateSchemaType) -> ModelType:
        """Update existing entity fields from update schema."""
        entity = await self.get(id)
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entity, field, value)
        return await self.repository.update(entity)

    async def remove(self, id: Any) -> bool:
        """Delete entity by ID."""
        await self.get(id)  # Validate existence
        return await self.repository.delete(id)
