from cmath import inf
from typing import TypeAlias
from loguru import logger
import nonebot
from pydantic import BaseModel
from motor import motor_asyncio

from .dbmodel import BasePid, BaseLolicon, BasePixiv, BaseFav

def get_right_db_client() -> motor_asyncio.AsyncIOMotorClient:
    client = nonebot.require("nonebot_plugin_navicat")
    client = client.mongodb_client
    assert(isinstance(client, motor_asyncio.AsyncIOMotorClient))
    return client

client = get_right_db_client()
db = client['db_pixiv']
c = db['pixiv_data']
c_info = db['lolicon_data']

class DBPidMgr:
    c: motor_asyncio.AsyncIOMotorCollection=None
    ModelMode:TypeAlias = BasePixiv
    def __init__(self, collection: motor_asyncio.AsyncIOMotorCollection) -> None:
        self.c = collection
    # CRUD
    async def insert_one(self, info: ModelMode):
        return await self.c.insert_one(info.dict())

    async def get_one_by_pid(self, pid: int):
        return await self.c.find_one({"pid": pid})

    async def update_one(self, info: ModelMode, upsert: bool = False):
        return await self.c.update_one({'pid': info.pid}, {'$set': info.dict()}, upsert=upsert)

    async def delete_one_by_pid(self, pid: int):
        return await self.c.delete_one({'pid': pid})

class DBLoliconMgr(DBPidMgr):
    ModelMode = BaseLolicon
    async def get_local_info_by_tags(self, tags: list[str]):
        db_query = [{'$match':
                    {"tags": {'$all': tags}},    # 条件
                    }] if tags else []
        db_query += [{'$sample': {'size': 1}}]
        cur = self.c.aggregate(db_query)
        res = await cur.to_list(1)
        if res:
            return BaseLolicon.parse_obj(res[0])
        raise ValueError("No match imgs")

class DBFavMgr(DBPidMgr):
    ModelMode = BaseFav
    pass

class DBMgrBuilder():
    @staticmethod
    def get_db_file()->DBPidMgr:
        return DBPidMgr(db['pixiv_data'])
    @staticmethod
    def get_db_lolicon() -> DBLoliconMgr:
        return DBLoliconMgr(db['lolicon_data'])
    @staticmethod
    def get_db_fav() -> DBFavMgr:
        return DBFavMgr(db['fav_data'])
