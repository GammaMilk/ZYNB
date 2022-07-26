import json
# from utils.http_utils import AsyncHttpx
import os
from pathlib import Path
from typing import Union
from urllib import response

import httpx
import nonebot
import nonebot.adapters.telegram as tg
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (Bot, Event, GroupMessageEvent,
                                         Message, MessageEvent,
                                         PrivateMessageEvent)
from nonebot.log import logger
from nonebot.params import ArgStr, CommandArg, State
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from PIL import Image, ImageDraw, ImageFont

from .config import *
from .utils import *

__zx_plugin_name__ = "apex"
__plugin_meta__ = PluginMetadata(
    name='apex',
    description='Apex 玩家查询',
    usage=f'''欢迎使用Apex查询
/aid [玩家id] 查询玩家信息
/ar 查询复制器
/amap 查询地图
/abind [玩家id] 绑定玩家
/apre 查询冲猎
此Bot配置的命令前缀：{" ".join(list(nonebot.get_driver().config.command_start))}
'''
)

amap = on_command("amap", priority=5, block=True)
areplicator = on_command("ar", priority=5, block=True)
apredator = on_command("apre", priority=5, block=True)
ainquire = on_command("aid", priority=5, block=True)
abind = on_command("abind", priority=5, block=True)


@ amap.handle()
async def amap_handler(bot: Bot, event: MessageEvent, state: T_State):
    '''
    查询APEX地图轮换
    '''
    url = f"https://api.mozambiquehe.re/maprotation?auth={Tool_Token}&version=1"
    # resp = requests.get(url)
    # retdata = json.loads(resp.text)
    async with httpx.AsyncClient() as client:
        retdata = await client.get(url)
        retdata = retdata.json()

    tmpimgs = []
    for data in retdata:
        if data == "control":
            continue
        current = retdata[data]["current"]
        nextmap = retdata[data]["next"]

        isHasImg(f"{Map_Path}/{current['code']}.png", current["asset"])

        im = Image.open(f"{Map_Path}/{current['code']}.png")
        x, y = im.size
        im = im.resize((960, 300), Image.ANTIALIAS)

        # addText(im, 50, GameMode_Dict[data], 20, 20)
        addText(im, 50, data, 20, 20)
        addText(im, 60, Map_Dict[current['code']] if current['code']
                in Map_Dict else current['map'], 20, 90)
        # if data != "ranked":
        #     addText(im, 80, f"剩余时间：{current['remainingTimer']}", 40, 350)
        addText(im, 30, f"剩余时间：{current['remainingTimer']}", 20, 170)
        addText(
            im, 30, f"下一轮换：{Map_Dict[nextmap['code']] if nextmap['code'] in Map_Dict else nextmap['map']}", 20, 220)

        tmpimg = f'{Temp_Path}/{data}_{current["code"]}.png'
        tmpimgs.append(tmpimg)
        im.save(tmpimg)

    # 设置画布(格式，尺寸，背景色)
    image = Image.new('RGB', (960, 1200), (255, 255, 255))
    logger.info(tmpimgs)
    for i, img in enumerate(tmpimgs):
        if i == 0:
            image.paste(Image.open(img), (0, 0))
        elif i == 1:
            image.paste(Image.open(img), (0, 300))
        elif i == 2:
            image.paste(Image.open(img), (0, 600))
        elif i == 3:
            image.paste(Image.open(img), (0, 900))

    image.save(f"{Temp_Path}/map_ok.png")
    image_file = f"file:///{Temp_Path}/map_ok.png"
    msg = f"[CQ:image,file={image_file}]"
    try:
        # await bot.send_group_msg(group_id=event.group_id, message=msg)
        await amap.finish(Message(msg))
    except Exception as e:
        logger.info(e)

# 复制器


@ areplicator.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    url = f"https://api.mozambiquehe.re/crafting?auth={Tool_Token}"
    # resp = requests.get(url)
    # resp = resp.text
    # retdata = json.loads(resp)
    # 使用httpx异步请求
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        retdata = resp.json()
    zday = retdata[0]["bundleContent"]
    zwek = retdata[1]["bundleContent"]
    items = [zday[0]["itemType"], zday[1]["itemType"],
             zwek[0]["itemType"], zwek[1]["itemType"]]
    image = Image.new('RGB', (800, 800), (255, 255, 255))
    for i, item in enumerate(items):
        localImg = f"{Make_Path}/{item['name']}.png"
        isHasImg(localImg, item["asset"])
        im = Image.open(localImg)
        im = im.resize((400, 400), Image.ANTIALIAS)
        if i == 0:
            image.paste(im, (0, 0))
        elif i == 1:
            image.paste(im, (400, 0))
        elif i == 2:
            image.paste(im, (0, 400))
        elif i == 3:
            image.paste(im, (400, 400))

    addText(image, 50, "当日", 350, 345)
    addText(image, 50, "本周", 350, 405)
    image.save(f"{Temp_Path}/mark_ok.png")
    image_file = f"file:///{Temp_Path}/mark_ok.png"
    msg = f"[CQ:image,file={image_file}]"
    try:
        # await bot.send_group_msg(group_id=event.group_id, message=msg)
        await areplicator.finish(Message(msg))
    except Exception as e:
        logger.info(e)

# 猎杀


@ apredator.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    url = f"https://api.mozambiquehe.re/predator?auth={Tool_Token}"
    # resp = requests.get(url)
    # resp = json.loads(resp.text)
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp = resp.json()
    try:
        ls = Image.open(f"{Template_Path}/ls.png")
        for i, res in enumerate(resp):
            rank = resp[res]
            name = "大逃杀" if res == "RP" else "竞技场"
            for j, ter in enumerate(rank):
                terr = rank[ter]
                lastRank = terr["foundRank"]
                rankScore = terr["val"]
                rankTotal = terr["totalMastersAndPreds"]
                x, y = 60 if i == 0 else 430, 650 + (j * 300)
                addText(ls, 40, f"最低排名：{lastRank}", x, y)
                addText(ls, 40, f"排位分数：{rankScore}", x, y + 50)
                addText(ls, 40, f"大师总数：{rankTotal}", x, y + 100)

        ls.save(f"{Temp_Path}/ls_ok.png")
        image_file = f"file:///{Temp_Path}/ls_ok.png"
        msg = f"[CQ:image,file={image_file}]"
        # await bot.send_group_msg(group_id=event.group_id, message=msg)
        await apredator.finish(Message(msg))
    except Exception as e:
        logger.info(e)
        await bot.send(f"出错了，要不再试一次？")

# 绑定


@ abind.handle()
async def _(event: Event, text: Message = CommandArg()):
    args = []
    if len(text) > 0:
        args = text[0].data['text'].split(' ')
    if len(args) < 1:
        await abind.send('绑定ID使用方式：/abind [OriginID]')
        return

    EA_ID = args[0]
    # response = requests.get(
    #     f"https://api.mozambiquehe.re/bridge?auth={Tool_Token}&player={EA_ID}&platform=PC")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.mozambiquehe.re/bridge?auth={Tool_Token}&player={EA_ID}&platform=PC")
    if response.status_code != 200:
        print(response.content.decode("utf-8"))
        await abind.send('EA id疑似有误!')
    else:
        QQ_EA = loadEAIDJson()
        QQ = event.get_user_id()
        QQ_EA[QQ] = EA_ID
        writeEAID(QQ_EA)
        QQ_NICKNAME = event.get_event_name()
        if isinstance(event, GroupMessageEvent):
            msg = f"绑定成功！\nQQ：{QQ}\n昵称：[CQ:at,qq={QQ}]\nEA id：{EA_ID}"
        else:
            msg = f"绑定成功！\nEA id：{EA_ID}"
        await abind.send(Message(msg))

# 查询玩家信息


@ ainquire.handle()
async def _(bot: Bot, event: Event, text: Message = CommandArg()):
    args = []
    uid = ""

    if len(text) > 0:
        args = text[0].data['text'].split(' ')
    response = None

    if len(args) >= 1:
        # response = requests.get(f"https://api.mozambiquehe.re/bridge?auth={Tool_Token}&player={args[0]}&platform=PC")
        # 此处改用httpx异步请求
        async with httpx.AsyncClient(proxies={"all://": None}) as client:
            response = await client.get(f"https://api.mozambiquehe.re/bridge?auth={Tool_Token}&player={args[0]}&platform=PC")
        uid = args[0]
        if response.status_code != 200:
            await ainquire.send('EA_ID疑似有误!')
            return
    else:
        QQ = event.get_user_id()
        QQ_EA = loadEAIDJson()
        if QQ_EA.get(QQ) is None:
            await ainquire.send(f'{QQ}未绑定EA账号!')
            return
        logger.info(QQ_EA[QQ])
        # response = requests.get(
        #     f"https://api.mozambiquehe.re/bridge?auth={Tool_Token}&player={QQ_EA[QQ]}&platform=PC")
        async with httpx.AsyncClient(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'},
            proxies={"all://": None}
        ) as client:
            response = await client.get(
                f"https://api.mozambiquehe.re/bridge?auth={Tool_Token}&player={QQ_EA[QQ]}&platform=PC",
                timeout=10)
        if response.status_code != 200:
            await ainquire.send('绑定的EA id疑似有误，要不...再试一次?')
            return
        uid = QQ_EA[QQ]
    response = json.loads(response.text)

    rankPimg = ""
    arenaPimg = ""
    img = Image.open(f"{Template_Path}/info.png")

    try:
        user = response["global"]
        toNextLevelPercent = user["toNextLevelPercent"] / 100
        # progressBar(img, (255, 255, 255), (130, 170, 0),
        #             1100, 185, 300, 20, toNextLevelPercent)
        addText(img, 44, str(toNextLevelPercent*100)+"%", 1100, 174)
        addText(img, 60, user["name"] if user["name"] else uid, 1080, 63)
        addText(img, 32, str(user["level"] if user["level"]
                < 500 else user["level"]), 780, 216, (0, 0, 0))
        for rk in range(2):
            rname = ["rank", "排位"] if rk == 1 else ["arena", "竞技场"]
            rank = user[rname[0]]
            rankName = rank["rankName"]
            rankDiv = rank["rankDiv"]
            rankImg = rank["rankImg"]

            rimgPath = f"{Rank_Path}/{rankName}{rankDiv}.png"
            isHasImg(rimgPath, rankImg)
            rimgdraw = Image.open(rimgPath).convert("RGBA")
            rimgdraw = rimgdraw.resize((250, 250), Image.ANTIALIAS)
            rimgdraw.save(rimgPath)

            if rk == 1:
                rankPimg = rimgPath
            else:
                arenaPimg = rimgPath
            ix, iy = (765, 600) if rk == 1 else (1200, 600)
            rankScore = rank["rankScore"]
            ladderPosPlatform = rank["ladderPosPlatform"]

            addText(img, 40, f"{rname[1]}：{rankScore}", ix, iy)
            addText(
                img, 40, f"猎杀排名：{str(ladderPosPlatform) if ladderPosPlatform > 0 else '无'}", ix, iy + 50)

        realtime = response["realtime"]
        addText(img, 40, "当前状态：", 680, 900)
        addText(img, 40, "在线" if realtime["isOnline"] else "离线", 900, 900)
        addText(img, 40, "正在游戏" if realtime["isInGame"] else "未在游戏", 1070, 900)
        addText(
            img, 40, "小队已满" if realtime["partyFull"] else "小队未满", 1300, 900)

        legends = response["legends"]["selected"]
        LegendName = legends["LegendName"]
        icon = legends["ImgAssets"]["icon"]
        iconPath = f"{Legend_Path}/{LegendName}.png"
        if not isHasImg(iconPath, icon):
            nopic = Image.open(f"{Template_Path}/nopic.png")
            addText(nopic, 50, Legend_Dict[LegendName], 230, 150, (0, 0, 0))
            iconPath = f"{Temp_Path}/{LegendName}_nopic.png"
            nopic.save(iconPath)

        addText(img, 60, Legend_Dict[LegendName]
                if LegendName in Legend_Dict else LegendName, 170, 33)
        lengData = legends["data"]
        for i, dat in enumerate(lengData):
            y = 120 + (i * 75)
            addText(
                img, 30, f"{isHasKey(dat['name'],Tracker)[1] if isHasKey(dat['name'],Tracker)[0] else dat['name']}：", 100, y)
            addText(img, 30, str(dat["value"]), 500, y)

        icoPimgh = Image.open(iconPath).convert("RGBA")
        rankPimgh = Image.open(rankPimg).convert("RGBA")
        arenaPimgh = Image.open(arenaPimg).convert("RGBA")

        img.paste(rankPimgh, (760, 320), mask=rankPimgh)
        img.paste(arenaPimgh, (1200, 320), mask=arenaPimgh)
        img.paste(icoPimgh, (0, 270), mask=icoPimgh)
        img.save(f"{Temp_Path}/{uid}_info.png")
        image_file = f"file:///{Temp_Path}/{uid}_info.png"
        msg = f"[CQ:image,file={image_file}]"
        # await bot.send_group_msg(group_id=event.group_id, message=msg)
        await ainquire.send(Message(msg))
    except Exception as e:
        logger.info(e)
        # await bot.send_group_msg(group_id=event.group_id, message="未查到或出现错误")
        await ainquire.send("未查到或出现错误")
