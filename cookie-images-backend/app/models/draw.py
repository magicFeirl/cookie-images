from pydantic import BaseModel


class DrawDocItem(BaseModel):
    poster_uid: int
    title: str
    description: str
    pictures: list[str]
    count: int
    ctime: int
    view: int
    like: int
    dyn_id: str