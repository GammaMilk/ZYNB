import json
import time
from typing import Any

# from utils.http_utils import AsyncHttpx
import httpx
import nonebot
import nonebot.adapters.telegram as tg
import nonebot.config
from nonebot import get_driver, on_command, on_startswith, require
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.log import logger
from nonebot.params import ArgStr, CommandArg, State
from nonebot.typing import T_State
from pydantic import BaseModel, Extra

aps = require("nonebot_plugin_apscheduler")
if aps:
    from nonebot_plugin_apscheduler import scheduler


class Config(BaseModel, extra=Extra.ignore):
    vpn_signin_cookie: dict
    superusers: list[str]


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

sign_handler = on_command("signin", priority=5, block=True)
plugin_config = Config.parse_obj(get_driver().config)
# logger.error(plugin_config)
# sign_cookie = json.loads(plugin_config.vpn_signin_cookie)
sign_cookie = plugin_config.vpn_signin_cookie
superuser = int(plugin_config.superusers[0])
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"


def time_stamp_to_readable(time_stamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_stamp))


for key, value in sign_cookie.items():
    if isinstance(value, (int, float)):
        sign_cookie[key] = str(value)


async def _sign_main():
    async with httpx.AsyncClient(cookies=sign_cookie, headers={
            'User-Agent': _UA}) as cli:
        try:
            res = await cli.post("https://jinkela.lol/user/checkin")
            if res.status_code == 200:
                if json_obj := res.json():
                    return json_obj['msg']
            elif res.status_code == 302:
                return "请更新Cookie"
        except Exception as err:
            logger.error(err)
            return "签到失败"
        return "签到失败"


def _sign_main_decorator(func):
    async def _sign_main_wrapper(bot, event, state):
        sign_res = await _sign_main()
        state['sign_result'] = sign_res
        await func(bot, event, state)
    return _sign_main_wrapper


@sign_handler.handle()
@_sign_main_decorator
async def _sign_qq_handler(bot: Bot, event: MessageEvent, state: T_State):
    await sign_handler.finish(state['sign_result'])


@sign_handler.handle()
@_sign_main_decorator
async def _sign_tg_handler(bot: tg.Bot, event: tg.Event, state: T_State):
    await sign_handler.finish(state['sign_result'])


# TODO: 添加手工传送cookie的方式更新cookie

@scheduler.scheduled_job('interval', days=1, id='sign_job')
async def every_day():
    bot = nonebot.get_bot()
    logger.info("签到开始")
    sign_res = await _sign_main()
    logger.info(sign_res)
    if superuser:
        _id = superuser
        await bot.call_api("send_private_msg", user_id=_id, message=sign_res)
