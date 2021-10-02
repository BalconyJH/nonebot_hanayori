<!-- markdownlint-disable MD033 MD041-->
<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/kanomahoro/images@main/logo.png" width="200" height="200"/>
</p>

<div align="center">

# HanayoriBot
<!-- markdownlint-disable-next-line MD036 -->
_✨ 基于NoneBot2的B站动态推送与开播提醒插件 ✨_

</div>

## 简介

本插件基于[NoneBot2](https://github.com/nonebot/nonebot2)与[go-cqhttp](https://github.com/Mrs4s/go-cqhttp),可以及时推送B站UP主动态至群聊；并且能够对B站主播的直播间状态进行实时监控，从而实现了主播开播提醒；有效避免了突击直播，无人问津的尴尬局面

名字由来：花寄女子寮(Hanayori Joshiryou) 花寄天下第一！！！！！（来自某花寄~~DD~~单推人）
+ 鹿乃ちゃん：B站(316381099)
+ 小东人魚Official：B站(441382432)
+ 花丸晴琉Official：B站(441381282)
+ 野野宫のののOfficial：B站(441403698)

## 特色

1. **轻依赖**：本插件在编写时尽量避免了采用使用第三方包，以减少依赖项
2. **轻量化**：本插件经由3个文件构成，可以快速集成至任何已有的机器人框架
3. **支持aarch64架构**：本插件在树莓派4B上能够正常运行，并且支持安卓平台的termux环境
4. **强权限管理**：本插件在编写时采用了强权限的设计，仅可由超级用户、群主、管理员进行操作
5. **平行数据库**：私聊好友、各群聊拥有独立的数据库，互不干扰
## 即刻开始
### B站视频教程
[【【HanayoriBot】十分钟拥有你的群聊 单推(DD)机器人-哔哩哔哩】](https://b23.tv/PbPAqE)
### 安装NoneBot2
完整文档可以在 [这里](https://v2.nonebot.dev/) 查看。

懒得看文档？下面是快速安装指南：

1. (可选)使用你喜欢的 Python 环境管理工具创建新的虚拟环境。
2. 使用 `pip` (或其他) 安装 NoneBot 脚手架。

   ```bash
   pip install nb-cli
   ```

3. 使用脚手架创建项目

   ```bash
   nb create
   ```
4. 请在创建项目时选用cqhttp适配器，并且按照文档完成最小实例的创建
   
### 配置文件示例
1. .env
   ```yml
   ENVIRONMENT=prod
   ```
2. .env.prod
   ```yml
   HOST=127.0.0.1
   PORT=8080
   SECRET=
   ACCESS_TOKEN=
   SUPERUSERS=[超级用户账户(你的QQ号,不是机器人的账户)]
   COMMAND_START=["","/"]
   NICKNAME=["","/"]
   COMMAND_SEP=["."]
   ```
3. 请务必安装以上示例配置你的Bot；go-cqhttp请自行参照官方文档配置
### 安装HanayoriBot
   1. pip安装
   ```bash
   pip install nonebot-plugin-hanayori
   ```
   请在你的bot.py文件中加入以下内容
   ```python
   nonebot.load_plugin("nonebot_plugin_hanayori")#添加此行
   nonebot.load_from_toml("pyproject.toml")#位于本行前
   ```
   2. 使用nb-cli安装(推荐)
  
   在你的Bot目录下执行：
   ```bash
   nb plugin install nonebot_plugin_hanayori
   ```
### 指令说明
以下所以指令在群聊中只允许超级用户(主人)、群主、管理员进行操作，私聊中不受限制
**在群聊中使用格式**：@机器人 指令 UID(如果指令要求的话) 
**在私聊中使用格式**：指令 UID(如果指令要求的话)
**所有指令如下：**
1. **关注 UID**
   添加新主播，UID为主播的B站UID
2. **取关 UID**
   取关主播，UID为主播的B站UID
3. **列表**
   显示当前关注列表
4. **开启动态 UID**
   开启B站动态推送
5. **关闭动态 UID**
   关闭B站动态推送
6. **开启直播 UID**
   开启开播提醒
7. **关闭直播 UID**
   关闭开播提醒
8. **开启全体 UID**
   开启开播@全体成员
9. **关闭全体 UID**
   关闭开播@全体成员
10. **帮助**
   顾名思义

### 遇到问题？
你可以直接提交issue，或者发送邮件到：kano@hanayori.top
### 效果展示

![效果1](https://cdn.jsdelivr.net/gh/kanomahoro/images@main/xiaoguo1.jpg)

![效果2](https://cdn.jsdelivr.net/gh/kanomahoro/images@main/xiaoguo2.jpg)
