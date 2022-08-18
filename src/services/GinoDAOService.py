from loguru import logger
from webbrowser import GenericBrowser
from gino import Gino
from Config import config

db = Gino()

async def init():
    address = config.PG_HOST
    port = config.PG_PORT
    database = config.PG_DBNAME
    user = config.PG_USER
    password = config.PG_PSWD
    if (not user and not password and not address and not port and not database):
        raise ValueError("\n" + "数据库配置未填写")
    i_bind = f"postgresql://{user}:{password}@{address}:{port}/{database}"
    try:
        await db.set_bind(i_bind)
        await db.gino.create_all()
        logger.info(f'Database loaded successfully!')
    except Exception as e:
        raise Exception(f'数据库连接错误.... {type(e)}: {e}')


async def disconnect():
    await db.pop_bind().close()