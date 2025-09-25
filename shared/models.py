from typing import Annotated

from pydantic import BaseModel, AfterValidator, Field


def ensure_end_gt_start(value: int, info):
    print(info)
    return value


class RangeModel(BaseModel):

    start: int = Field(default=0)
    end: Annotated[int, AfterValidator(ensure_end_gt_start)] = Field(default=0)
