from pydantic import BaseModel


class Session(BaseModel):
    clients: list[str]
    scene: str
