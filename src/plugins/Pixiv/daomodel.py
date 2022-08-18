from ast import Delete
import datetime
from email.policy import default
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import update,delete
from sqlalchemy.dialects.postgresql import ARRAY,insert

from services.GinoDAOService import db
from dbmodel import BaseLolicon

class LoliconDAOModel(db.Model):
    __tablename__ = "lolicon"

    id = db.Column(db.Integer(), primary_key=True)
    user_qq = db.Column(db.BigInteger(), nullable=False)
    group_id = db.Column(db.BigInteger())
    text = db.Column(db.Text())
    plain_text = db.Column(db.Text())
    create_time = db.Column(db.DateTime(timezone=True), nullable=False)

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
        found = await cls.query.where(cls.pid == loli.pid).gino.first()
        match (not not found, upsert):
            case (True,True):
                stmt = update(cls).where(cls.pid==loli.pid).values(**loli.dict())
            case (False,True):
                stmt = insert(cls).values(**loli.dict())
            case (True,False):
                stmt = None
            case (False,False):
                stmt = None
        if stmt:
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
        stmt = delete(cls).values(cls.pid == pid)
        return await stmt.gino.first()
