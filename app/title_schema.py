from pydantic import BaseModel


class TitleResponse(BaseModel):
    title: str
    author: str
    url: str
