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
testHandler = on_startswith("tt", priority=5, block=True)

# 地图


@helpHandler.handle()
async def helper_msg_handler(bot: Bot, event: MessageEvent, state: T_State):
    await helpHandler.finish(__plugin_usage__)


@helpHandler.handle()
async def h2(bot: tg.Bot, event: tg.Event, state: T_State):
    await helpHandler.finish(__plugin_usage__)


@testHandler.handle()
async def test_handler(bot: Bot, event: MessageEvent, state: T_State):
    msg = ET.Element("msg")
    # set msg.property
    msg.set("serviceID", "1")
    msg.set("templateID", "-1")
    msg.set("action", "web")
    msg.set("brief", "挂哥已经进群聊天")
    msg.set("sourceMsgId", "0")
    msg.set("url", "")
    msg.set("flag", "0")
    msg.set("adverSign", "0")
    msg.set("multiMsgFlag", "0")
    item = ET.SubElement(msg, "item")
    item.set("layout", "2")
    item.set("advertiser_id", "0")
    item.set("aid", "0")
    pic = ET.SubElement(item, "picture")
    pic.set("cover", "https://c2cpicdw.qpic.cn/offpic_new/389213129//389213129-2081305543-37978D947CED64571088B53CBD88D634/0?term=3")
    pic.set("w", "0")
    pic.set("h", "0")
    title = ET.SubElement(item, "title")
    title.text = "挂哥已经进群聊天"
    summary = ET.SubElement(item, "summary")
    summary.text = "注意言辞！"
    source = ET.SubElement(msg, "source")

    # dump
    xml_str = ET.tostring(msg, encoding="utf-8",
                          xml_declaration=True).decode("utf-8")
    logger.info(xml_str)
    # CQCODE encapsulation
    cqcode = "[CQ:xml,data=" + xml_str + ",resid=]"
    await bot.send(event, Message(cqcode))
