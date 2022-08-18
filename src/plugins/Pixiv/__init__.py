import io
import json
import os
import re
import sys
import time
import typing
from base64 import b64decode, b64encode
from typing import Any, Iterable

import httpx
import nonebot
import nonebot.adapters.telegram as tg
import nonebot.exception
from fastapi import Depends
from nonebot import get_driver, on_command, on_startswith
from nonebot.adapters.onebot.v11 import (Bot, Event, GroupMessageEvent,
                                         Message, MessageEvent, MessageSegment,
                                         PrivateMessageEvent)
from nonebot.log import logger
from nonebot.params import ArgStr, CommandArg, Depends, State
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from PIL import Image
from pydantic import BaseModel, Extra

from . import imgmgr
from .imgmodel import PxImage

__plugin_meta__ = PluginMetadata(
    name='pixiv',
    description='获取简单的图片',
    usage='''/p [pid|tag]\n/fav [pid] 设置收藏\n/pfav 获得收藏\npdel [pid]''',
    extra={'version': '3.1'}
)


class Config(BaseModel, extra=Extra.ignore):
    pixiv_proxy: str
    no_setu: typing.List[str]


no_setu = Config.parse_obj(get_driver().config).no_setu
pixiv_proxy = Config.parse_obj(get_driver().config).pixiv_proxy
proxy_used = True


async def gen_client_async() -> httpx.AsyncClient:
    """生成httpx客户端

    Yields:
        httpx.AsyncClient: httpx客户端
    """
    p = {'all://': None} if not proxy_used else None
    async with httpx.AsyncClient(proxies=p, timeout=12) as client:
        yield client

pxv = on_command("p", priority=5, block=True)
fav = on_command("fav", priority=5, block=True)
pfav = on_command("pfav", priority=5, block=True)
pdel = on_command("pdel", priority=5, block=True)

def formatted_img(img:PxImage):
    if len(img.img) > 5*1024*1024:
        logger.warning(f"图片大于5Mb，将会被压缩")
        img.img = imgmgr.compress_img(img.img)
    img.img += b'\x00'
    rawimg = MessageSegment.image(img.img)
    pid = MessageSegment.text(f"PID: {img.pid}\n")
    url = MessageSegment.text(f"URL: {img.url}\n")
    return pid+url+rawimg

@pdel.handle()
async def _(
    state: T_State,
    args: Message = CommandArg()
):
    strsmsg = args.extract_plain_text().split(" ")
    try:
        pids = list(map(int,strsmsg))
    except:
        await pdel.finish("Format error.\nplz use <SPACE> to split integer pids.")
    logger.debug(f"{type(args)}DEL: {pids}")
    ret = []
    for pid in pids:
        ret.append(await imgmgr.del_img(pid))
    await pdel.finish(",".join(ret))

@pxv.handle()
async def _(
    state: T_State,
    args: Message = CommandArg(),
    client: httpx.AsyncClient = Depends(gen_client_async)
):
    strsmsg = args.extract_plain_text().split(" ")
    logger.debug(f"{type(args)}ARGS: {args}")
    if len(strsmsg) >= 1 and strsmsg[0]:
        state['pid'] = strsmsg
    else:
        # random one
        img = await imgmgr.get_img_by_tags([], client)
        await pxv.finish(formatted_img(img))


@pxv.got('pid')
async def _(
        state: T_State,
        client: httpx.AsyncClient = Depends(gen_client_async)
):
    pid = state['pid']
    if isinstance(pid, Message):
        pid = pid.extract_plain_text().split(' ')
    assert(isinstance(pid, list))
    logger.warning(f"{type(pid)}pid: {pid}")
    isPid = not not re.match(r'^\d+$', pid[0])  # 判断是否为pid
    imgs:list[PxImage] = []
    try:
        if isPid:  # 这是数字pid
            ts = [] #Tasks
            for p in pid:
                isPid = True if re.match(r'^\d+$', p) else False
                if isPid: #每项检验是否为数字
                    ts.append(imgmgr.get_img_by_pid(int(p), client))
            for t in ts:
                im = await t
                if im:
                    imgs += [im]
        else:  # 此Pid是Tags
            if pid[0].lower() in no_setu:
                await pxv.finish(f"抱歉，{pid}暂时不支持搜索哦")
            pid = [x.strip("'").strip('"') for x in pid]
            imgs += [await imgmgr.get_img_by_tags(pid, client)]
    except ValueError as e:
        await pxv.finish(str(e))
    if imgs:
        for soloimg in imgs:
            await pxv.send(formatted_img(soloimg))
