"""Abstract Generic Repository Interface following Repository Pattern."""

from typing import Generic, List, Optional, TypeVar, Any, Sequence

ModelType = TypeVar("ModelType")


class IRepository(Generic[ModelType]):
    """Generic Abstract Base Repository Interface."""

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Retrieve a single entity by primary key."""
        raise NotImplementedError

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Retrieve a paginated list of entities."""
        raise NotImplementedError

    async def create(self, entity: ModelType) -> ModelType:
        """Persist a new entity instance."""
        raise NotImplementedError

    async def update(self, entity: ModelType) -> ModelType:
        """Update an existing entity instance."""
        raise NotImplementedError

    async def delete(self, id: Any) -> bool:
        """Delete an entity by primary key."""
        raise NotImplementedError

    async def count(self) -> int:
        """Count total entities in storage."""
        raise NotImplementedError
