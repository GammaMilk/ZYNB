import re
from typing import Iterable
import httpx
from pydantic import PostgresDsn
from . import dbmgr, cfg

_cache_dir = cfg.get_local_img_cache_path()
_pxv_proxy = cfg.get_pxv_proxy()
_UA = cfg.get_UA()


async def get_original_url_by_pid(pid: int) -> str:
    """根据pid获取原图url
    Args:
        pid: 图片id
    Returns:
        str: 原图url
    """
    async with httpx.AsyncClient() as client:
        URL_ART = f"https://www.pixiv.net/artworks/{pid}"
        res = await client.get(URL_ART, headers={"User-Agent": _UA})
        html = res.content.decode("utf-8")
        regex = '''https://i.pximg.net/img-original/.*?[jp][pn]g'''
        img_url = re.findall(regex, html)
        if img_url:
            img_url = img_url[0]
            return img_url
        raise ValueError("pid无效")


async def get_proxy_url_by_pid(pid: int) -> str:
    """根据pid获取图片的代理url
    Args:
        pid: 图片id
    Returns:
        str: 代理url
    """
    return await get_original_url_by_pid(pid).replace("i.pximg.net", _pxv_proxy)


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
    img_original_url = await get_original_url_by_pid(pid)
    img_url = img_original_url.replace("i.pximg.net", _pxv_proxy)
    img_suffix = img_url.split(".")[-1]
    async with httpx.AsyncClient() as client:
        res = await client.get(img_url, headers={"User-Agent": _UA})
        img = res.content
    # 第三步：如果获取成功，则缓存到本地
    if img:
        item = dbmgr.DBModelPixiv(
            pid=pid, local=True, url=img_original_url, lpath=f"{_cache_dir}/{pid}.{img_suffix}")
        with open(item.lpath, "wb") as f:
            f.write(img)
        await c.insert_one(item.dict())
    return img


async def get_img_by_info(info: dbmgr.DBModelLolicon) -> bytes:
    """根据info获取图片本体
    Args:
        info: 图片信息
    Returns:
        bytes: 图片
    """
    url = info.url.replace("i.pximg.net", _pxv_proxy)
    img_suffix = url.split(".")[-1]
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers={"User-Agent": _UA})
        img = res.content
    if img:
        item = dbmgr.DBModelPixiv(
            pid=info.pid, local=True, url=info.url, lpath=f"{_cache_dir}/{info.pid}.{img_suffix}")
        with open(item.lpath, "wb") as f:
            f.write(img)
        await dbmgr.get_db_collection().insert_one(item.dict())
    return img


async def get_img_by_tags(tags: Iterable[str]) -> bytes:
    """根据标签获取图片本体
    Args:
        tags: 标签
    Returns:
        bytes: 图片
    """
    info = await get_img_info_by_tags(tags)
    return await get_img_by_info(info)


async def get_img_info_by_tags(tags: Iterable[str]) -> dbmgr.DBModelLolicon:
    """根据标签获取图片id
    Args:
        tags: 标签
    Returns:
        int: 图片id
    """
    # 第一步 在线模式获取数据
    async with httpx.AsyncClient() as client:
        url_search = r"https://api.lolicon.app/setu/v2"
        method = "POST"
        data = {"tag": list(tags)}
        r = await client.request(method=method, url=url_search, json=data)
        r = r.json()
        if not r['data']:
            raise ValueError("未找到相关图片")
        r = r['data'][0]
        isR18 = r['r18'] or 'R-18' in r['tags']
        r['r18'] = isR18
        r['url'] = r['urls']['original'].replace("i.pixiv.re", "i.pximg.net")
    ret = dbmgr.DBModelLolicon.parse_obj(r)
    # 第二步 保存数据到本地数据库
    c = dbmgr.get_db_database()['lolicon_data']
    # 检查数据库中是否已经有这个pid
    dbres = await c.find_one({"pid": ret.pid})
    if not dbres:
        c.insert_one(ret.dict())
    return ret
