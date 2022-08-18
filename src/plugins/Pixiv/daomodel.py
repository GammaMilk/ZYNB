import datetime
from typing import List, Optional
from pydantic import BaseModel
import gino
import nonebot
from sqlalchemy import update,delete
from sqlalchemy.dialects.postgresql import ARRAY,insert
from .dbmodel import BaseLolicon


def get_right_db_client() -> gino.Gino:
    client = nonebot.require("GinoDAO")
    client = client.pgdb
    #print(type(client))
    #assert(isinstance(client, gino.Gino))
    return client

db = get_right_db_client()

class LoliconDAOModel(db.Model):
    __tablename__ = "lolicon"

    pid = db.Column(db.BigInteger(), nullable=False,
                    primary_key=True, unique=True)
    uid = db.Column(db.BigInteger(), nullable=False)
    title = db.Column(db.Text())
    author = db.Column(db.Text())
    r18 = db.Column(db.Boolean())
    width = db.Column(db.Integer())
    height = db.Column(db.Integer())
    tags = db.Column(ARRAY(db.Text()))
    url = db.Column(db.Text())
    
    @classmethod
    async def insert_many(cls, lolis: List[BaseLolicon]):
        for loli in lolis:
            print(loli.pid)
            query = cls.query.where(cls.pid == loli.uid)
            instanceLoli = await query.gino.first()
            if instanceLoli:
                continue
            u = cls()
            for x,y in dict(loli).items():
                setattr(u,x,y)
            await u.create()
    
    @classmethod
    async def insert_one(cls, loli:BaseLolicon):
        if type(loli) != BaseLolicon:
            raise ValueError()
        query = cls.query.where(cls.pid == loli.uid)
        instanceLoli = await query.gino.first()
        if instanceLoli:
            return
        u = cls()
        for x,y in dict(loli).items():
            setattr(u,x,y)
        await u.create()
    
    @classmethod
    async def query_tags(cls, tags:List[str]):
        if not tags:
            return []
        query = cls.query
        query = query.where(cls.tags.contains(tags))
        # for tag in tags:
        #     query = query.where(cls.title.contains(tag) | cls.author.contains(tag))
        query = query.order_by(db.func.random()).limit(10)
        return await query.gino.all()

    @classmethod
    async def update_one(cls, loli:BaseLolicon, upsert=False):
        if not isinstance(loli,BaseLolicon):
            raise ValueError()
        found = not not (await cls.query.where(cls.pid == loli.pid).gino.first())
        if found:
            stmt = update(cls).where(cls.pid==loli.pid).values(**loli.dict())
        else:
            stmt = insert(cls).values(**loli.dict()) if upsert else None
        
        if stmt is not None:
            executing = await stmt.gino.first()
    
    @classmethod
    async def get_one_by_pid(cls, pid:int):
        if not isinstance(pid,int):
            raise ValueError()
        query = cls.query.where(cls.pid==pid)
        return await query.gino.first()
    
    @classmethod
    async def insert_one(cls, loli:BaseLolicon):
        if not isinstance(loli,BaseLolicon):
            raise ValueError()
        stmt = insert(cls).values(**loli.dict())
        return await stmt.gino.first()
    
    @classmethod
    async def delete_one(cls, pid:int):
        if not isinstance(pid,int):
            raise ValueError()
        stmt = delete(cls).where(cls.pid == pid)
        return await stmt.gino.first()
