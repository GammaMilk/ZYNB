import os
import toml

_PATH_LOCAL_IMG_CACHE = ""
_PXV_PROXY = "zjlnb.gmk.icu"


def get_local_img_cache_path() -> str:
    """生成本地图片缓存路径

    Returns:
        str: 默认路径或者已经配置好的路径
    """
    if not _PATH_LOCAL_IMG_CACHE:
        return f"{os.path.dirname(__file__)}/ImgCache"
    return _PATH_LOCAL_IMG_CACHE


def get_pxv_proxy() -> str:
    """获取pixiv的代理url

    Returns:
        str: 代理url
    """
    if not _PXV_PROXY:
        return "i.pixiv.re"
    return _PXV_PROXY.removeprefix("https://").removeprefix("http://").removesuffix("/")


def get_UA() -> str:
    """获取pixiv的UA

    Returns:
        str: UA
    """
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
