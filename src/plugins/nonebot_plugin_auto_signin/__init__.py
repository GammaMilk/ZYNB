import html
import json
import os
import time
from typing import Any, Union
from urllib.parse import urlencode

# from utils.http_utils import AsyncHttpx
import httpx
import nonebot
import nonebot.adapters.telegram as tg
import nonebot.config
from nonebot import get_driver, on_command, on_startswith, require
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, Message
from nonebot.log import logger
from nonebot.params import ArgStr, CommandArg, State
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
from pydantic import BaseModel, Extra, ValidationError

aps = require("nonebot_plugin_apscheduler")
if aps:
    from nonebot_plugin_apscheduler import scheduler


class Config(BaseModel, extra=Extra.ignore):
    vpn_signin_cookie: dict
    superusers: list[str]


__plugin_meta__ = PluginMetadata(
    name='signin',
    description='vnp签到',
    usage='''/signin\n/src [cookie]''',
    extra={'version': '3.1'}
)

sign_handler = on_command("signin", priority=5, block=True)
cookie_refresher = on_command("src", priority=5, block=True)

plugin_config = Config.parse_obj(get_driver().config)
# logger.error(plugin_config)
# sign_cookie = json.loads(plugin_config.vpn_signin_cookie)
superuser = int(plugin_config.superusers[0])
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"


def time_stamp_to_readable(time_stamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_stamp))

def cookie_str2dict(cookie_str) -> dict:
    logger.debug(cookie_str)
    cookie_dict = {}
    for cookie_item in cookie_str.split(";"):
        cookie_item = cookie_item.strip()
        if cookie_item:
            key, value = cookie_item.split("=", 1)
            cookie_dict[key] = value
    return cookie_dict

def load_cookie(path:Union[os.PathLike,str]) -> dict:
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("")
        return {}
    with open(path, "r") as f:
        cookie_str = f.read()
    return cookie_str2dict(cookie_str)

async def _sign_main(sign_cookie:dict=None):
    if sign_cookie is None:
        jkl_path = os.path.join(os.path.dirname(__file__), 'jinkela.cookie')
        sign_cookie = load_cookie(jkl_path)
    logger.info(sign_cookie)
    async with httpx.AsyncClient(cookies=sign_cookie, headers={
            'User-Agent': _UA}) as cli:
        try:
            res = await cli.post("https://jinkela.lol/user/checkin")
            if res.status_code == 200:
                if json_obj := res.json():
                    return json_obj['msg']
            elif res.status_code == 302:
                logger.warning(f"{res.headers['Location']}")
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

@scheduler.scheduled_job('interval', days=0.5, id='sign_job')
async def every_day():
    bot = nonebot.get_bot()
    logger.info("签到开始")
    sign_res = await _sign_main()
    logger.info(sign_res)
    if superuser:
        _id = superuser
        await bot.call_api("send_private_msg", user_id=_id, message=sign_res)


@cookie_refresher.handle()
async def cookie_refresher_handler(
    bot: Bot, 
    event: MessageEvent, 
    state: T_State, 
    msg:Message=CommandArg()
    ):
    msg = msg.extract_plain_text()
    try: # test valid?
        sign_cookie = cookie_str2dict(msg)
        res = await _sign_main(sign_cookie)
        if ('失败' in res )or ('ookie' in res):
            raise ValueError('cookie无效:['+res+']')
    except Exception as err:
        logger.error(err)
        await cookie_refresher.finish(str(err))
    # cookie valid, save it
    jkl_path = os.path.join(os.path.dirname(__file__), 'jinkela.cookie')
    with open(jkl_path, "w") as f:
        f.write(msg)
    await cookie_refresher.finish("Cookie已更新:" + res)

