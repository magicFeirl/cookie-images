from pydantic import BaseModel

from .draw import DrawDocItem


class BaseResponse(BaseModel):
    pn: int
    ps: int
    code: int
    message: str


class DrawResponse(BaseResponse):
    data: list[DrawDocItem]
