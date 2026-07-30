"""Abstract Generic Service Interface following Clean Architecture Application Layer."""

from typing import Generic, List, Optional, TypeVar, Sequence, Any

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class IService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic Abstract Service Interface."""

    async def get(self, id: Any) -> Optional[ModelType]:
        """Fetch entity by ID."""
        raise NotImplementedError

    async def get_multi(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Fetch multiple entities with pagination."""
        raise NotImplementedError

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create new entity using creation DTO."""
        raise NotImplementedError

    async def update(self, id: Any, obj_in: UpdateSchemaType) -> ModelType:
        """Update existing entity using update DTO."""
        raise NotImplementedError

    async def remove(self, id: Any) -> bool:
        """Delete entity by ID."""
        raise NotImplementedError
