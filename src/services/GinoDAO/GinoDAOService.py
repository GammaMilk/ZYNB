from loguru import logger
from gino import Gino
import nonebot

driver: nonebot.Driver = nonebot.get_driver()
config: nonebot.config.Config = driver.config

db = Gino()

pgsql_opened: bool = False

if getattr(config, "pg_host", None):
    nonebot.export().pgdb = db

@driver.on_startup
async def init():
    global pgsql_opened
    pgsql_opened = True

    i_bind = f"postgresql://{config.pg_user}:{config.pg_pswd}@{config.pg_host}:{config.pg_port}/{config.pg_dbname}"
    try:
        await db.set_bind(i_bind)
        await db.gino.create_all()
        logger.info(f'PostgreSQL Database loaded successfully!')
    except Exception as e:
        raise Exception(f'数据库连接错误.... {type(e)}: {e}')

@driver.on_shutdown
async def disconnect():
    global pgsql_opened
    pgsql_opened = False
    logger.info('PostgreSQL Service Shutting down...')
    await db.pop_bind().close()
