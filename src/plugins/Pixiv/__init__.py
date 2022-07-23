import os
import sys
import re
import time
from typing import Any
from fastapi import Depends
import nonebot
from nonebot import get_driver, on_command, on_startswith
from nonebot.typing import T_State
from nonebot.params import State, CommandArg, ArgStr
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, Event, GroupMessageEvent, PrivateMessageEvent, MessageSegment
import nonebot.adapters.telegram as tg
from nonebot.log import logger
# from utils.http_utils import AsyncHttpx
import json
import httpx

from pydantic import BaseModel, Extra
from . import imgmgr


__zx_plugin_name__ = "pixiv_helper"
__plugin_usage__ = """
usage：
    p [pixiv_id]
""".strip()
__plugin_des__ = "p"
__plugin_cmd__ = ["p"]
__plugin_version__ = 3
__plugin_author__ = "MerkyGao"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": __plugin_cmd__,
}

# logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} {level} {message}",
#            level="INFO", filter=__zx_plugin_name__)


class Config(BaseModel, extra=Extra.ignore):
    pixiv_proxy: str


pxv = on_command("p", priority=5, block=True)
try:
    plugin_config = Config.parse_obj(get_driver().config)
    pxv_proxy = plugin_config.pixiv_proxy.removeprefix(
        "https://").removeprefix("http://").removesuffix("/")

except Exception as e:
    pxv_proxy = "i.pixiv.re"
    logger.warning("pixiv_proxy is empty. fallback to {}".format(pxv_proxy))

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
# 初始化缓存目录
cache_dir = f"{os.path.dirname(__file__)}/ImgCache"
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)


@pxv.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    if not pxv_proxy:
        await pxv.finish("未设置pixiv_proxy !")
    strsmsg = event.message.extract_plain_text().split(" ")
    if len(strsmsg) >= 2:
        state['pid'] = strsmsg[1]


@pxv.got('pid', prompt="请键入pid")
async def _(bot: Bot, event: MessageEvent, state: T_State):
    # TODO 增加多个pid一同识别
    pid = state['pid']
    isPid = True if re.match(r'^\d+$', pid) else False  # 判断是否为pid
    try:
        if isPid:
            img = await imgmgr.get_img_by_pid(int(pid))
        else:  # 此Pid是Tag
            img = await imgmgr.get_img_by_tags([pid])
    except ValueError as e:
        await pxv.finish("pid不合法")
    except Exception as e:
        await pxv.finish("获取图片失败,其他错误")
    if img:
        await pxv.finish(MessageSegment.image(img))
