from cmath import inf
import datetime
from turtle import up
from typing import TypeAlias
from loguru import logger
import nonebot
from pydantic import BaseModel
from motor import motor_asyncio

from .dbmodel import BasePid, BaseLolicon, BasePixiv, BaseFav
from .daomodel import LoliconDAOModel

def __sa_entry_to_dict(entry):
    entry_dict = {}
    columns = entry.__table__.columns
    for column in columns:
        item_key = str(column).split('.')[1]
        item_value = getattr(entry, item_key)
        if type(item_value) == datetime:
            item_value = str(item_value)
        entry_dict[item_key] = item_value
    return entry_dict

class DBLoliconMgr:
    ModelMode:TypeAlias = BaseLolicon
    # CRUD
    async def insert_one(self, info: ModelMode):
        return await LoliconDAOModel.insert_one(info)

    async def get_one_by_pid(self, pid: int):
        return __sa_entry_to_dict(await LoliconDAOModel.get_one_by_pid(int(pid)))

    async def update_one(self, info: ModelMode, upsert: bool = False):
        return await LoliconDAOModel.update_one(info,upsert=upsert)

    async def delete_one_by_pid(self, pid: int):
        return await LoliconDAOModel.delete_one(pid)

    async def get_local_info_by_tags(self, tags: list[str]):
        res = await LoliconDAOModel.query_tags(tags)
        if res:
            return __sa_entry_to_dict(res[0])


# TODO: 搁置
# class DBFavMgr(DBPidMgr):
#     ModelMode = BaseFav
#     pass

class DBMgrBuilder():
    @staticmethod
    def get_db_lolicon() -> DBLoliconMgr:
        return DBLoliconMgr()
