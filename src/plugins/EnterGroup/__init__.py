import time
from typing import Any
import nonebot
from nonebot import get_driver, on_command, on_endswith, on_keyword, on_startswith
from nonebot.typing import T_State
from nonebot.params import State, CommandArg, ArgStr
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, Event, GroupMessageEvent, PrivateMessageEvent
import nonebot.adapters.telegram as tg
from nonebot.log import logger
import json
import httpx
from . import makemsg


__zx_plugin_name__ = "已经进群聊天"
__plugin_usage__ = """
usage：
    []已经进群聊天 ([])
""".strip()
__plugin_des__ = __zx_plugin_name__
__plugin_cmd__ = []
__plugin_version__ = 3
__plugin_author__ = "MerkyGao"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": __plugin_cmd__,
}


_sign_handler = on_keyword("已经进群聊天", priority=5, block=True)


@_sign_handler.handle()
async def _sign_qq_handler(bot: Bot, event: MessageEvent, state: T_State):
    strsmsg = event.message.extract_plain_text().replace("已经进群聊天", "").split(" ")
    defalut_describe = "注意言辞！"
    defalut_img = "https://c2cpicdw.qpic.cn/offpic_new/389213129//389213129-2081305543-37978D947CED64571088B53CBD88D634/0?term=3"
    if len(strsmsg) == 1:
        c = makemsg.makemsg(strsmsg[0], defalut_describe, defalut_img)
    elif len(strsmsg) == 2:
        c = makemsg.makemsg(strsmsg[0], strsmsg[1], defalut_img)
    elif len(strsmsg) == 3:
        c = makemsg.makemsg(strsmsg[0], strsmsg[1], strsmsg[2])
    elif len(strsmsg) == 4:
        c = makemsg.makemsg(strsmsg[0], strsmsg[1], strsmsg[2], strsmsg[3])
    else:
        await _sign_handler.finish("参数错误！")
    await _sign_handler.finish(Message(c))
