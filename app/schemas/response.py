from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class GenericResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "Success"
    data: T | None = None
