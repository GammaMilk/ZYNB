# 配置文件如何写？

```toml
HOST=127.0.0.1 #这是你本机的地址，不用改
PORT=8080 #这是端口。需要和go-cqhttp那边保持同步。默认就是8080.被占用了就改成其他的。
LOG_LEVEL=DEBUG # 日志输出等级
FASTAPI_RELOAD=true # 热重载
driver=~fastapi+~httpx 
telegram_bots =[{"token": ""}] #tg机器人的token。项目中暂时没有使用tg，所以暂时保留。
apex_token= # apex查询服务的令牌。需要自己申请！
vpn_signin_cookie= # 已弃用。
pixiv_proxy= # 已弃用

MONGODB_HOST=127.0.0.1 # MongoDB的地址。这里默认了本机
MONGODB_PORT=27017 # MongoDB的端口。这里给的也是默认
MONGODB_USER= # 连接本机时不需要用户名和密码。
MONGODB_PASSWORD=

SUPERUSERS=["114514"] # 超级用户的企鹅帐号。大致应该填写成你自己的主号罢
no_setu=["zhenxun","xiaozhenxun"] # 当搜索setu时触发这些词时，不提供setu！
```

### ApexToken申请：

> 原项目：[AreCie/Apex_Tool: APEX英雄QQ群查询插件，适用于真寻Bot (github.com)](https://github.com/AreCie/Apex_Tool)
>
> 此处被本项目修改

Token需要在这里申请：

[API Portal (apexlegendsapi.com)](https://portal.apexlegendsapi.com/)

