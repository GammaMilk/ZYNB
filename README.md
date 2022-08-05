# ZYNB!

[English Version](./docs/README.ENG.md)

这是一个厨力项目。~~单纯是觉得隔壁的小真寻真是太可爱了QwQ！~~

受到一些同学的启发，感谢这个项目 [https://github.com/HibiKier/zhenxun_bot](https://github.com/HibiKier/zhenxun_bot) 给了我极大的动力和勇气去写另一个机器人。虽然不太完善罢。但是也采用了一些一个苦逼大学生还没有学到的寄术。作者（我就一个人）也只能照葫芦画瓢罢（悲）。

## 安装

- ### 确保环境中有poetry。如果没有，按照以下的命令安装。

  #### osx / linux / bashonwindows install instructions

```sh
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

  #### windows powershell install instructions

```powershell
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
```

>来自：https://python-poetry.org/docs/

- ### 确保环境中有MongoDB。如果没有，到以下网站下载安装。

> https://www.mongodb.com/try/download/community

- ### 确保有go-cqhttp的配置。如果没有，到Mrs4s的项目中看看吧！

> https://docs.go-cqhttp.org/guide/quick_start.html

- ### 克隆代码

  ```sh
  git clone https://github.com/GammaMilk/ZYNB.git
  cd ZYNB
  ```

- ### 安装依赖，初始化

  Linux/Unix...

  ```sh
  poetry install
  sh ./init.sh
  ```

  Windows:
  ```powershell
  poetry install
  ```

  然后手动把该重命名的文件重命名。如：`RENAME_THIS_FILE_TO_.env.dev` 重命名为 `.env.dev`.


- ### 改写配置文件

  依照[配置文件如何写？](./docs/config.md)

- ### 运行！

  ```sh
  poetry run nb run
  ```

## 感谢

- go-cqhttp [GitHub/Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
- nonebot v2 [GitHub/nonebot/nonebot2](https://github.com/nonebot/nonebot2)
- ApexTool 一个apex英雄的查询工具[GitHub/AreCie/Apex_Tool](https://github.com/AreCie/Apex_Tool)
- zhenxun_bot 一个可爱的机器人，本工程灵感源泉 [GitHub/HibiKier/zhenxun_bot](https://github.com/HibiKier/zhenxun_bot)

## 其他
- [ ] 正考虑迁移到PostgreSQL
- [ ] 把安装脚本改了