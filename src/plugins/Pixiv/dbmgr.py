from cmath import inf
from loguru import logger
import nonebot
from pydantic import BaseModel
from motor import motor_asyncio


class DBBaseModelPid(BaseModel):
    pid: int


class DBModelPixiv(DBBaseModelPid):
    """
    Pixiv图片缓存数据库模型类
    """
    pid: int
    local: bool
    url: str
    lpath: str


class DBModelLolicon(DBBaseModelPid):
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
c_info = db['lolicon_data']


def get_db_database() -> motor_asyncio.AsyncIOMotorDatabase:
    """获取数据库Database链接实例

    Returns:
        motor_asyncio.AsyncIOMotorDatabase: Database
    """
    return db


def get_db_file_collection() -> motor_asyncio.AsyncIOMotorCollection:
    """获取数据库Collection链接实例

    Returns:
        motor_asyncio.AsyncIOMotorCollection: Collection
    """
    return c


async def sync_lolicon_db(info: DBModelLolicon):
    dbres = await c_info.find_one({"pid": info.pid})
    if not dbres:
        c_info.insert_one(info.dict())


async def get_local_info_by_tags(tags: list[str]):
    db_query = [{'$match':
                 {"tags": {'$all': tags}},    # 条件
                 }] if tags else []
    db_query += [{'$sample': {'size': 1}}]
    cur = c_info.aggregate(db_query)
    res = await cur.to_list(1)
    if res:
        return DBModelLolicon.parse_obj(res[0])
    raise ValueError("No match imgs")


class DBPidMgr:
    client = get_right_db_client()
    db = client['db_pixiv']

    def __init__(self, collection: motor_asyncio.AsyncIOMotorCollection) -> None:
        self.c = collection
    # CRUD

    async def insert_one(self, info: DBBaseModelPid):
        return await self.c.insert_one(info.dict())

    async def get_one_by_pid(self, pid: int):
        return await self.c.find_one({"pid": pid})

    async def update_one(self, info: DBBaseModelPid, upsert: bool = False):
        return await self.c.update_one({'pid': info.pid}, {'$set': info.dict()}, upsert=upsert)

    async def delete_one_by_pid(self, pid: int):
        return await self.c.delete_one({'pid': pid})


def get_db_file_mgr() -> DBPidMgr:
    return DBPidMgr(db['pixiv_data'])


def get_db_lolicon_mgr() -> DBPidMgr:
    return DBPidMgr(db['lolicon_data'])
