import imp
from pydantic import BaseModel, Extra
from nonebot import get_driver

class PG_config(BaseModel, extra=Extra.ignore):
    PG_HOST:str
    PG_PORT:str
    PG_USER:str
    PG_PSWD:str
    PG_DBNAME:str

config=PG_config.parse_obj(get_driver().config)