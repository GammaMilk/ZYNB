from base64 import b64decode, b64encode
import os
import io
import sys
import re
import time
from typing import Any, Iterable
import typing
import PIL
from PIL import Image
from fastapi import Depends
import nonebot
from nonebot import get_driver, on_command, on_startswith
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
from nonebot.params import State, CommandArg, ArgStr
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, Event, GroupMessageEvent, PrivateMessageEvent, MessageSegment
import nonebot.adapters.telegram as tg
import nonebot.exception
from nonebot.params import Depends
from nonebot.log import logger
# from utils.http_utils import AsyncHttpx
import json
import httpx

from pydantic import BaseModel, Extra
from . import imgmgr

__plugin_meta__ = PluginMetadata(
    name='pixiv',
    description='获取简单的图片',
    usage='''/p [pid|tag]''',
    extra={'version': '3.1'}
)


class Config(BaseModel, extra=Extra.ignore):
    pixiv_proxy: str
    no_setu: typing.List[str]


no_setu = Config.parse_obj(get_driver().config).no_setu


async def gen_client_async():
    async with httpx.AsyncClient() as client:
        yield client

pxv = on_command("p", priority=5, block=True)


@pxv.handle()
async def _(
    state: T_State,
    args: Message = CommandArg(),
    client: httpx.AsyncClient = Depends(gen_client_async)
):
    strsmsg = args.extract_plain_text().split(" ")
    logger.debug(f"{type(args)}ARGS: {args}")
    if len(strsmsg) >= 1 and strsmsg[0]:
        state['pid'] = strsmsg[0]
    else:
        # random one
        img = await imgmgr.get_img_by_tags([], client)
        await pxv.finish(MessageSegment.image(img))


@pxv.got('pid')
async def _(
        state: T_State,
        client: httpx.AsyncClient = Depends(gen_client_async)
):
    # TODO 增加多个pid一同识别
    pid = state['pid']
    if isinstance(pid, Message):
        pid = pid.extract_plain_text()
    logger.warning(f"{type(pid)}pid: {pid}")
    isPid = True if re.match(r'^\d+$', pid) else False  # 判断是否为pid
    img = None
    try:
        if isPid:
            img = await imgmgr.get_img_by_pid(int(pid), client)
        else:  # 此Pid是Tag
            if pid.lower() in no_setu:
                await pxv.finish(f"抱歉，{pid}暂时不支持搜索哦")
            img = await imgmgr.get_img_by_tags([pid], client)
    except ValueError as e:
        await pxv.finish(str(e))
    if img:
        if len(img) > 5*1024*1024:  # 图片大于5Mb
            logger.warning(f"图片大于5Mb，将会被压缩")
            img = imgmgr.compress_img(img)
        img += b'\x00'
        await pxv.finish(MessageSegment.image(img))
