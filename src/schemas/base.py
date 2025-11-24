from typing import Any, Sequence, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")
ModelT = TypeVar("ModelT", bound="BaseModel")


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate_list(
        cls: type[ModelT], items: Sequence[Any]
    ) -> Sequence[ModelT]:
        return [cls.model_validate(item) for item in items]
