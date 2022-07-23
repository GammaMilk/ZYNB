import re
import httpx
from . import dbmgr, cfg

_cache_dir = cfg.get_local_img_cache_path()
_pxv_proxy = cfg.get_pxv_proxy()
_UA = cfg.get_UA()


async def get_proxy_url_by_pid(pid: int) -> str:
    """根据pid获取图片的代理url
    Args:
        pid: 图片id
    Returns:
        str: 代理url
    """
    async with httpx.AsyncClient() as client:
        URL_ART = f"https://www.pixiv.net/artworks/{pid}"
        res = await client.get(URL_ART, headers={"User-Agent": _UA})
        html = res.content.decode("utf-8")
        regex = '''https://i.pximg.net/img-original/.*?[jp][pn]g'''
        img_url = re.findall(regex, html)
        if img_url:
            img_url = img_url[0].replace("i.pximg.net", _pxv_proxy)
            return img_url
        raise ValueError("pid无效")


async def get_img_by_pid(pid: int) -> bytes:
    """根据pid获取图片本体
    Args:
        pid: 图片id
    Returns:
        bytes: 图片
    """
    # 第一步：检查是否存在于缓存中
    c = dbmgr.get_db_collection()
    item = await c.find_one({"pid": pid})
    if item:
        item = dbmgr.DBModelPixiv.parse_obj(item)
        if item.local:
            with open(item.lpath, "rb") as f:
                return f.read()
    # 第二步：如果不存在，则从pixiv获取
    img_url = await get_proxy_url_by_pid(pid)
    img_suffix = img_url.split(".")[-1]
    async with httpx.AsyncClient() as client:
        res = await client.get(img_url, headers={"User-Agent": _UA})
        img = res.content
    # 第三步：如果获取成功，则缓存到本地
    if img:
        item = dbmgr.DBModelPixiv(
            pid=pid, local=True, url=img_url, lpath=f"{_cache_dir}/{pid}.{img_suffix}")
        with open(item.lpath, "wb") as f:
            f.write(img)
        await c.insert_one(item.dict())
    return img
