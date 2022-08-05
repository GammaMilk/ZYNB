from pydantic import BaseModel


class DBBaseModelPid(BaseModel):
    pid: int
    url: str


class DBModelPixiv(DBBaseModelPid):
    """
    Pixiv图片缓存数据库模型类
    """
    pid: int
    local: bool
    url: str
    lpath: str


class DBModelLolicon(DBBaseModelPid):
    """
    Lolicon数据库模型类(r18保存之前*必须检验*)
    """
    pid: int
    uid: int
    title: str
    author: str
    r18: bool
    width: int
    height: int
    tags: list[str]
    url: str

class DBModelFav(DBBaseModelPid):
    """
    收藏数据库模型类
    """
    pass