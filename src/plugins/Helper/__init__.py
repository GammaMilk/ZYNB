import nonebot
from nonebot import on_command, on_startswith
from nonebot.typing import T_State
from nonebot.params import State, CommandArg, ArgStr
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, Event, GroupMessageEvent, PrivateMessageEvent
import nonebot.adapters.telegram as tg
from nonebot.log import logger
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
# from utils.http_utils import AsyncHttpx
import json
import requests
import httpx
import xml.etree.ElementTree as ET

__zx_plugin_name__ = "APEX查询工具2"
__plugin_usage__ = """
usage：
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
    await helpHandler.finish(__plugin_usage__)


@helpHandler.handle()
async def h2(bot: tg.Bot, event: tg.Event, state: T_State):
    await helpHandler.finish(__plugin_usage__)


@th.handle()
async def test_handler(bot: Bot, event: MessageEvent, state: T_State):
    msgstrs = event.message.extract_plain_text().split(" ")
    if len(msgstrs) == 1:
        pass
    else:
        state['echo'] = msgstrs[1]
    #TODO 


@th.got('echo', prompt="Input your echo message:")
async def _(
    bot: Bot, 
    event: MessageEvent, 
    state: T_State, 
    echo: str = ArgStr('echo')
    ):
    await th.send(echo)


@th.got('xhello', prompt="Input your xhello message:")
async def _(
    bot: Bot, 
    event: MessageEvent, 
    state: T_State, 
    xhello: str = ArgStr('xhello')
    ):
    await th.send(xhello)
