import nonebot
from pydantic import BaseModel
from motor import motor_asyncio


class DBModelPixiv(BaseModel):
    """
    Pixiv图片缓存数据库模型类
    """
    pid: int
    local: bool
    url: str
    lpath: str


class DBModelLolicon(BaseModel):
    """
    Lolicon数据库模型类(r18保存之前*必须检验*)
    """
    pid: int
    uid: int
    title: str
    author: str
    r18: bool
    width: int
    height: int
    tags: list[str]
    url: str


def get_right_db_client() -> motor_asyncio.AsyncIOMotorClient:
    client = nonebot.require("nonebot_plugin_navicat")
    client = client.mongodb_client
    assert(isinstance(client, motor_asyncio.AsyncIOMotorClient))
    return client


client = get_right_db_client()
db = client['db_pixiv']
c = db['pixiv_data']


def get_db_database() -> motor_asyncio.AsyncIOMotorDatabase:
    """获取数据库Database链接实例

    Returns:
        motor_asyncio.AsyncIOMotorDatabase: Database
    """
    return db


def get_db_collection() -> motor_asyncio.AsyncIOMotorCollection:
    """获取数据库Collection链接实例

    Returns:
        motor_asyncio.AsyncIOMotorCollection: Collection
    """
    return c
