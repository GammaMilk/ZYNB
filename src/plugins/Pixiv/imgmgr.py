from cmath import log
import re
from tkinter.messagebox import NO
from typing import Iterable, Optional
import httpx
from sqlalchemy import false
from . import dbmgr, cfg
from .imgmodel import PxImage
from nonebot.log import logger
from PIL import Image
import io

_cache_dir = cfg.get_local_img_cache_path()
_pxv_proxy = cfg.get_pxv_proxy()
_UA = cfg.get_UA()
db_file_mgr = dbmgr.DBMgrBuilder.get_db_file()
db_lolicon_mgr = dbmgr.DBMgrBuilder.get_db_lolicon()


def print_func_name(func):
    def wrapper(*args, **kwargs):
        logger.debug(f"{func.__name__},START")
        res = func(*args, **kwargs)
        logger.debug(f"{func.__name__},END")
        return res
    return wrapper


@print_func_name
async def get_img_from_local(pid: int) -> PxImage:
    """根据pid获取本地图片本体
    Args:
        pid: 图片id
    Returns:
        PxImage: 图片
    """
    item = await db_file_mgr.get_one_by_pid(pid)
    logger.info(f"图片正从本地加载：{item}")
    if item:
        item = dbmgr.DBModelPixiv.parse_obj(item)
        if item.local:
            logger.info(f"从本地获取图片：{item.lpath}")
            with open(item.lpath, "rb") as f:
                return PxImage(img=f.read(),pid=pid,url=item.url)
        else:
            raise ValueError("该pid对应图片不在本地")
    else:
        raise ValueError(f"数据库中没有：{pid}")


@print_func_name
async def get_info_by_pid(
    pid: int,
    client: httpx.AsyncClient
) -> dbmgr.DBModelLolicon:
    """生成图片信息
    !会同步lolicon数据库!

    Args:
        pid (int): 图片id
        client (httpx.AsyncClient): httpx客户端

    Returns:
        dbmgr.DBModelLolicon: 图片大部分信息
    """
    URL_ART = f"https://px2.rainchan.win/json/{pid}"
    res = await client.get(URL_ART, headers={"User-Agent": _UA})
    res = res.json()
    if res['error']:
        raise ValueError(f"获取原图url失败：{res['message']}")
    res = res['body']
    logger.debug(f"获取到图片info:{res['illustTitle']}")
    info = dbmgr.DBModelLolicon(
        pid=pid,
        uid=res['userId'],
        title=res['illustTitle'],
        author=res['userAccount'],
        r18=False,
        width=res['width'],
        height=res['height'],
        tags=[x['tag'] for x in res['tags']['tags']],
        url=res['urls']['original']
    )
    info.r18 = 'R-18' in info.tags
    await db_lolicon_mgr.update_one(info, upsert=True)
    return info


def get_proxyurl_by_url(url: str) -> str:
    """根据url获取代理url

    Args:
        url (str): 使用代理服务器进行图片获取

    Returns:
        str: 使用代理服务器地址的图片url
    """
    return url.replace("i.pximg.net", _pxv_proxy)


@print_func_name
async def get_img_by_pid(
    pid: int, 
    client: Optional[httpx.AsyncClient] = None
    ) -> PxImage:
    """根据pid获取图片本体
    Args:
        pid: 图片id
    Returns:
        PxImage: 图片
    """
    pid = int(pid)
    # 第一步：检查是否存在于缓存中
    try:
        img = await get_img_from_local(pid)
        return img
    except Exception as e:
        logger.info(f"{e}图片在本地加载失败，正在联网加载：{pid}")
        pass
    # 第二步：如果不存在，则从pixiv获取
    use_arg_client = client is not None
    if not use_arg_client:
        client = httpx.AsyncClient(
            headers={"User-Agent": _UA}, proxies={"all://": None})
    logger.debug(f"下载图片信息：{pid}")
    img_info = await get_info_by_pid(pid, client)
    img_original_url = img_info.url
    img_suffix = img_original_url.split(".")[-1]
    logger.debug(f"通过info加载图片：{img_info.pid}{img_info.title}")
    img = await get_img_by_info(img_info, client)
    # TODO img类型检验
    if not use_arg_client:
        await client.__aexit__()
    return img


@print_func_name
async def get_img_by_info(
    info: dbmgr.DBModelLolicon,
    client: httpx.AsyncClient
) -> PxImage:
    """根据info获取图片本体
    Args:
        info: 图片信息
    Returns:
        PxImage: 图片
    """
    try:
        img = await get_img_from_local(info.pid)
        logger.debug(f"图片已经从本地加载：{info.pid}")
        return img
    except:
        logger.info(f"图片本地加载失败，正在重新加载：{info.pid}")
        pass
    url = info.url.replace("i.pximg.net", _pxv_proxy)
    img_suffix = url.split(".")[-1]
    logger.debug(f"从互联网下载图片：{url}")
    res = await client.get(url, headers={"User-Agent": _UA})
    img = res.content
    if img:
        item = dbmgr.DBModelPixiv(
            pid=info.pid, local=True, url=info.url, lpath=f"{_cache_dir}/{info.pid}.{img_suffix}")
        with open(item.lpath, "wb") as f:
            logger.debug(f"图片下载成功，正在保：{info.pid}")
            f.write(img)
        logger.debug(f"更新数据库：{info.pid}")
        await db_file_mgr.update_one(item, upsert=True)
    img = PxImage(img=img, pid=info.pid, url=info.url)
    return img


async def get_img_by_tags(
    tags: Iterable[str],
    client: Optional[httpx.AsyncClient] = None
) -> PxImage:
    """根据标签获取图片本体
    Args:
        tags: 标签
        client: (可选)httpx异步客户端
    Returns:
        PxImage: 图片
    """
    use_arg_client = client is not None
    if not use_arg_client:
        client = httpx.AsyncClient(
            headers={"User-Agent": _UA},
            proxies={"all://": None})
    info = await get_info_by_tags(tags, client=client)
    img = await get_img_by_info(info, client=client)
    if not use_arg_client:
        await client.__aexit__()
    return img


async def get_info_by_tags(
    tags: Iterable[str],
    client: httpx.AsyncClient
) -> dbmgr.DBModelLolicon:
    """根据标签获取图片id
    !会同步lolicon数据库!
    Args:
        tags: 标签
    Returns:
        int: 图片id
    """
    # 第一步 在线模式获取数据
    logger.info(f"在线模式获取图片信息：{tags}")
    url_search = r"http://x6.gmk.icu/setu/v2"
    method = "GET"
    data = {"tag": list(tags)}
    try:
        # r = await client.request(method=method, url=url_search, json=data, timeout=10)
        tags_query = "".join([f"tag={tag}&" for tag in tags])
        req_url = f"{url_search}?{tags_query}"
        r = await client.get(req_url)
        r = r.json()
        if not r['data']:
            raise ValueError("未找到相关图片")
        r = r['data'][0]
        isR18 = r['r18'] or ('R-18' in r['tags'])
        r['r18'] = isR18
        r['url'] = r['urls']['original'].replace("i.pixiv.re", "i.pximg.net")
        ret = dbmgr.DBModelLolicon.parse_obj(r)
        # 第二步 保存数据到本地数据库
        logger.debug(f"同步数据库 {ret.pid}")
        await db_lolicon_mgr.update_one(ret, upsert=True)
    except Exception as e:
        # Fall back to local mode
        logger.error(f"NETWORK ERROR, FALLBACK TO LOCAL MODE{e}")
        ret = await dbmgr.get_local_info_by_tags(tags)
    return ret


def compress_img(img: bytes):
    img2 = Image.open(io.BytesIO(img))
    fileio = io.BytesIO()
    rgb_im = img2.convert('RGB')
    rgb_im.save(fileio, format='JPEG', quality=90)
    return fileio.getvalue()


async def get_original_url_by_pid(pid: int) -> str:
    raise DeprecationWarning("该函数已废弃,请使用get_img_info_by_pid")
    """根据pid获取原图url
    Args:
        pid: 图片id
    Returns:
        str: 原图url
    """
    # 弃用原生接口
    async with httpx.AsyncClient() as client:
        URL_ART = f"https://www.pixiv.net/artworks/{pid}"
        res = await client.get(URL_ART, headers={"User-Agent": _UA})
        html = res.content.decode("utf-8")
        regex = '''https://i.pximg.net/img-original/.*?[jgp][pin][gf]'''
        img_url = re.findall(regex, html)
        if img_url:
            img_url = img_url[0]
            logger.debug(f"获取原图url:{img_url}")
            return img_url
