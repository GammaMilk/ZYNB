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
c_info = db['lolicon_data']


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


async def sync_lolicon_db(info: DBModelLolicon):
    dbres = await c_info.find_one({"pid": info.pid})
    if not dbres:
        c.insert_one(info.dict())


async def get_local_info_by_tag(tags: list[str]):
    db_query = [{'$match':
                 {"tags": {'$all': tags}},    # 条件
                 }] if tags else []
    db_query += [{'$sample': {'size': 1}}]
    cur = c_info.aggregate(db_query)
    res = await cur.to_list(1)
    if res:
        return DBModelLolicon.parse_obj(res[0])
    raise ValueError("No match imgs")
