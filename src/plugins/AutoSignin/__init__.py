import time
from typing import Any
import nonebot
from nonebot import get_driver, on_command, on_startswith
from nonebot.typing import T_State
from nonebot.params import State, CommandArg, ArgStr
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message, Event, GroupMessageEvent, PrivateMessageEvent
import nonebot.adapters.telegram as tg
from nonebot.log import logger
# from utils.http_utils import AsyncHttpx
import json
import httpx

from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    vpn_signin_cookie: dict


__zx_plugin_name__ = "VNP自动签到"
__plugin_usage__ = """
usage：
    无需使用
""".strip()
__plugin_des__ = "签到模块"
__plugin_cmd__ = ["signin"]
__plugin_version__ = 3
__plugin_author__ = "MerkyGao"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": __plugin_cmd__,
}

_sign_handler = on_command("signin", priority=5, block=True)
plugin_config = Config.parse_obj(get_driver().config)
# logger.error(plugin_config)
# sign_cookie = json.loads(plugin_config.vpn_signin_cookie)
sign_cookie = plugin_config.vpn_signin_cookie
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"


def time_stamp_to_readable(time_stamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_stamp))


for key, value in sign_cookie.items():
    if isinstance(value, (int, float)):
        sign_cookie[key] = str(value)


async def _sign_main():
    async with httpx.AsyncClient(cookies=sign_cookie, headers={
            'User-Agent': _UA}, proxies={"https://": "http://localhost:10809"}) as cli:
        try:
            r = await cli.post("https://jinkela.lol/user/checkin")
            if r.status_code == 200:
                if js := r.json():
                    return js['msg']
        except Exception as e:
            logger.error(e)
            return "签到失败"
        return "签到失败"


def _sign_main_decorator(func):
    async def _sign_main_wrapper(bot, event, state):
        s = await _sign_main()
        state['sign_result'] = s
        await func(bot, event, state)
    return _sign_main_wrapper


@_sign_handler.handle()
@_sign_main_decorator
async def _sign_qq_handler(bot: Bot, event: MessageEvent, state: T_State):
    await _sign_handler.finish(state['sign_result'])


@_sign_handler.handle()
@_sign_main_decorator
async def _sign_tg_handler(bot: tg.Bot, event: tg.Event, state: T_State):
    await _sign_handler.finish(state['sign_result'])


# TODO: 添加手工传送cookie的方式更新cookie
