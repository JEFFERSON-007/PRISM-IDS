"""Base Pydantic v2 Schema Definition."""

from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

DataType = TypeVar("DataType")


class BaseResponseModel(BaseModel, Generic[DataType]):
    """Standardized API Success Response Envelope."""

    model_config = ConfigDict(from_attributes=True)

    success: bool = True
    message: Optional[str] = "Success"
    data: Optional[DataType] = None
    request_id: Optional[str] = None
