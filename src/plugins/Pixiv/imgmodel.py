from pydantic import BaseModel


class PxImage(BaseModel):
    img:bytes
    pid:int
    url:str
