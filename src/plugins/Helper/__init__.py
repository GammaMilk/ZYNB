import json
from lib2to3.pgen2 import driver
from pydoc import cli
from xml.dom.minidom import TypeInfo

import httpx
import nonebot
import nonebot.adapters.telegram as tg
from motor import motor_asyncio
from nonebot import on_command, on_startswith
from nonebot.adapters.onebot.v11 import (Bot, Event, GroupMessageEvent,
                                         Message, MessageEvent,
                                         PrivateMessageEvent)
from nonebot.log import logger
from nonebot.params import ArgStr, CommandArg, State
from nonebot.typing import T_State
from pydantic import BaseModel


def get_right_db_client() -> motor_asyncio.AsyncIOMotorClient:
    client = nonebot.require("nonebot_plugin_navicat")
    client = client.mongodb_client
    assert(isinstance(client, motor_asyncio.AsyncIOMotorClient))
    return client


client = get_right_db_client()
db = client['db_pixiv']
c = db['pixiv_data']


class DBModelPixiv(BaseModel):
    pid: int
    local: bool
    orl: str
    lpath: str


__zx_plugin_name__ = "帮助和测试模块"
__plugin_usage__ = """
usage:
    帮助：（未完成）
""".strip()
__plugin_des__ = "帮助模块"
__plugin_cmd__ = ["help"]
__plugin_version__ = 3
__plugin_author__ = "MerkyGao"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ["help"],
}

helpHandler = on_command("help", priority=5, block=True)
th = on_startswith("tt", priority=5, block=True)

# 地图


@helpHandler.handle()
async def helper_msg_handler(bot: Bot, event: MessageEvent, state: T_State):
    pass


@helpHandler.handle()
async def h2(bot: tg.Bot, event: tg.Event, state: T_State):
    await helpHandler.finish(__plugin_usage__)


@th.handle()
async def test_handler(bot: Bot, event: MessageEvent, state: T_State):
    pass
