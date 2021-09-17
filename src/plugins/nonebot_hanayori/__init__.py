from dataclasses import MISSING
from nonebot import on_command
from nonebot import rule
from nonebot import on_request
from nonebot import on_notice
from nonebot.adapters import Bot,Event
from nonebot.adapters.cqhttp.event import MessageEvent, Status
from nonebot.rule import to_me
from nonebot.adapters.cqhttp.permission import GROUP_ADMIN, GROUP_OWNER, PRIVATE_FRIEND
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot,Message,GroupMessageEvent,bot,FriendRequestEvent,GroupRequestEvent,GroupDecreaseNoticeEvent
from nonebot import require
from . import data_source
from . import model
import asyncio
import nonebot
model.Init()
live_index=0
dynamic_index=0
scheduler = require('nonebot_plugin_apscheduler').scheduler
@scheduler.scheduled_job('interval',seconds=15,id='bilibili_live')
async def live():#定时推送直播间状态
    if model.Empty():
        return
    (schedBot,)=nonebot.get_bots().values()
    global live_index
    anchors=model.GetAnchorList()
    live_index %=len(anchors)
    for index in range(live_index,len(anchors)):
        if anchors[index][3]==1:
            break
        live_index+=1
    if live_index==len(anchors):
        return
    status,live_status,content=await data_source.LiveRoomInfo(anchors[live_index][0])
    if status!=0 or anchors[live_index][4]==live_status:
        live_index+=1
        return
    model.UpdateLive(anchors[live_index][0],live_status)
    cards=model.GetALLCard(anchors[live_index][0])
    for card in cards:
        if card[3]==1:#允许推送直播
            if card[1]==1:#是群聊
                if card[4]==1:#需要@全体成员
                    await schedBot.call_api('send_msg',**{
                        'message':'[CQ:at,qq=all]'+content,
                        'group_id':card[0]
                    })
                else:#不需要@全体成员
                    await schedBot.call_api('send_msg',**{
                        'message':content,
                        'group_id':card[0]
                    })
            else:#私聊
                await schedBot.call_api('send_msg',**{
                    'message':content,
                    'user_id':card[0]
                })
    live_index+=1
@scheduler.scheduled_job('interval',seconds=15,id='bilibili_dynamic')
async def dynamic():#定时推送最新用户动态
    if model.Empty():
        return
    (schedBot,)=nonebot.get_bots().values()
    global dynamic_index
    anchors=model.GetAnchorList()
    dynamic_index %=len(anchors)
    status,dynamic_id,content= await data_source.LatestDynamicInfo(anchors[dynamic_index][0])
    if status!=0 or anchors[dynamic_index][2]==dynamic_id:
        dynamic_index+=1
        return
    model.UpdateDynamic(anchors[dynamic_index][0],dynamic_id)
    cards=model.GetALLCard(anchors[dynamic_index][0])
    for card in cards:
        if card[2]==1:#允许推送动态
            if card[1]==1:#是群聊
                await schedBot.call_api('send_msg',**{
                    'message':content,
                    'group_id':card[0]
                })
            else:#私聊
                await schedBot.call_api('send_msg',**{
                    'message':content,
                    'user_id':card[0]
                })
    dynamic_index+=1
adduser = on_command('关注',rule=to_me(),priority=5,permission=GROUP_ADMIN|GROUP_OWNER|PRIVATE_FRIEND|SUPERUSER,)
@adduser.handle()#添加主播
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    is_group=int(isinstance(event,GroupMessageEvent))
    id=event.get_session_id()
    if not id.isdigit():
        id=id.split('_')[1]
    args = str(event.get_message()).strip()
    msg = '指令格式错误！请按照：关注 UID'
    if args!='' and args.isdigit():
        anchor=model.GetAnchorInfo(args)
        if len(anchor)!=0:
                status=model.AddCard(args,id,is_group,anchor[3])
                if status==0:
                    msg='{}({})添加成功！'.format(anchor[1],args) #待测试
                else:
                    msg='{}({})已存在！'.format(anchor[1],args) #待测试
        else:
            status,username,liveroom=await data_source.UserInfo(args)
            if(status==0):
                model.AddNewAnchor(args,username,liveroom)
                model.AddCard(args,id,is_group,liveroom)
                msg='{}({})添加成功！'.format(username,args) #待测试
            else:
                msg='{} UID不存在或网络错误！'.format(args)
    Msg = Message(msg)
    await adduser.finish(Msg)

removeuser = on_command('取关',rule=to_me(),priority=5,permission=GROUP_ADMIN|GROUP_OWNER|PRIVATE_FRIEND|SUPERUSER,)
@removeuser.handle()#取关主播
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    is_group=int(isinstance(event,GroupMessageEvent))
    id=event.get_session_id()
    if not id.isdigit():
        id=id.split('_')[1]
    args = str(event.get_message()).strip()
    msg = '指令格式错误！请按照：取关 UID'
    if args!='' and args.isdigit():
        anchor=model.GetAnchorInfo(args)
        if len(anchor)==0:
            msg = '{} 主播不存在！请检查UID是否错误'.format(args)
        else:
            status=model.DeleteCard(args,id,is_group)
            if status!=0:
                msg='{}({})不在当前群组/私聊关注列表'.format(anchor[1],args)
            else:
                msg='{}({})删除成功！'.format(anchor[1],args)
    Msg = Message(msg)
    await adduser.finish(Msg)

alllist = on_command('列表',rule=to_me(),priority=5,permission=GROUP_ADMIN|GROUP_OWNER|PRIVATE_FRIEND|SUPERUSER,)
@alllist.handle()#显示当前群聊/私聊中的关注列表
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    is_group=int(isinstance(event,GroupMessageEvent))
    id=event.get_session_id()
    if not id.isdigit():
        id=id.split('_')[1]
    msg='主播名称(UID)\n'
    content=''
    if not id.isdigit():
        id=id.split('_')[1]
    anchor=model.GetAnchorList()
    for index in anchor:
        card=model.GetCard(index[0],id,is_group)
        if len(card)!=0:
            content+='{}({})\n{} {} {}\n'.format(index[1],index[0],str(card[2]).replace('1','动态:开').replace('0','动态:关'),str(card[3]).replace('1','直播:开').replace('0','直播:关'),str(card[4]).replace('1','全体成员:开').replace('0','全体成员:关'))
    if content=='':
        msg='当前群聊/私聊关注列表为空！'
    else:
        msg=msg+content
    Msg=Message(msg)
    await alllist.finish(Msg)

ondynamic = on_command('开启动态',rule=to_me(),priority=5,permission=GROUP_ADMIN|GROUP_OWNER|PRIVATE_FRIEND|SUPERUSER,)
@ondynamic.handle()#启动动态推送
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    is_group=int(isinstance(event,GroupMessageEvent))
    id=event.get_session_id()
    if not id.isdigit():
        id=id.split('_')[1]
    args = str(event.get_message()).strip()
    msg = '指令格式错误！请按照：开启动态 UID'
    if args!='' and args.isdigit():
        anchor=model.GetAnchorInfo(args)
        if len(anchor)==0:
            msg = '{} 主播不存在！请检查UID是否错误'.format(args)
        else:
            card=model.GetCard(args,id,is_group)
            if len(card)==0:
                msg='{}({})不在当前群组/私聊关注列表！'.format(anchor[1],args)
            else:
                model.DynamicON(args,id,is_group)
                msg='{}({})开启动态推送！'.format(anchor[1],args)
    Msg=Message(msg)
    await ondynamic.finish(Msg)

offdynamic = on_command('关闭动态',rule=to_me(),priority=5,permission=GROUP_ADMIN|GROUP_OWNER|PRIVATE_FRIEND|SUPERUSER,)
@offdynamic.handle()#启动动态推送
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    is_group=int(isinstance(event,GroupMessageEvent))
    id=event.get_session_id()
    if not id.isdigit():
        id=id.split('_')[1]
    args = str(event.get_message()).strip()
    msg = '指令格式错误！请按照：关闭动态 UID'
    if args!='' and args.isdigit():
        anchor=model.GetAnchorInfo(args)
        if len(anchor)==0:
            msg = '{} 主播不存在！请检查UID是否错误'.format(args)
        else:
            card=model.GetCard(args,id,is_group)
            if len(card)==0:
                msg='{}({})不在当前群组/私聊关注列表！'.format(anchor[1],args)
            else:
                model.DynamicOFF(args,id,is_group)
                msg='{}({})关闭动态推送！'.format(anchor[1],args)
    Msg=Message(msg)
    await offdynamic.finish(Msg)

onlive = on_command('开启直播',rule=to_me(),priority=5,permission=GROUP_ADMIN|GROUP_OWNER|PRIVATE_FRIEND|SUPERUSER,)
@onlive.handle()#启动直播推送
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    is_group=int(isinstance(event,GroupMessageEvent))
    id=event.get_session_id()
    if not id.isdigit():
        id=id.split('_')[1]
    args = str(event.get_message()).strip()
    msg = '指令格式错误！请按照：开启直播 UID'
    if args!='' and args.isdigit():
        anchor=model.GetAnchorInfo(args)
        if len(anchor)==0:
            msg = '{} 主播不存在！请检查UID是否错误'.format(args)
        else:
            card=model.GetCard(args,id,is_group)
            if len(card)==0:
                msg='{}({})不在当前群组/私聊关注列表！'.format(anchor[1],args)
            else:
                if anchor[3]!=1:
                    msg='{}({})还未开启直播间！'.format(anchor[1],args)
                else:
                    model.LiveON(args,id,is_group)
                    msg='{}({})开启直播推送！'.format(anchor[1],args)
    Msg=Message(msg)
    await onlive.finish(Msg)

offlive = on_command('关闭直播',rule=to_me(),priority=5,permission=GROUP_ADMIN|GROUP_OWNER|PRIVATE_FRIEND|SUPERUSER,)
@offlive.handle()#启动直播推送
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    is_group=int(isinstance(event,GroupMessageEvent))
    id=event.get_session_id()
    if not id.isdigit():
        id=id.split('_')[1]
    args = str(event.get_message()).strip()
    msg = '指令格式错误！请按照：关闭直播 UID'
    if args!='' and args.isdigit():
        anchor=model.GetAnchorInfo(args)
        if len(anchor)==0:
            msg = '{} 主播不存在！请检查UID是否错误'.format(args)
        else:
            card=model.GetCard(args,id,is_group)
            if len(card)==0:
                msg='{}({})不在当前群组/私聊关注列表！'.format(anchor[1],args)
            else:
                if anchor[3]!=1:
                    msg='{}({})还未开启直播间！'.format(anchor[1],args)
                else:
                    model.LiveOFF(args,id,is_group)
                    msg='{}({})关闭直播推送！'.format(anchor[1],args)
    Msg=Message(msg)
    await offlive.finish(Msg)

onat = on_command('开启全体',rule=to_me(),priority=5,permission=GROUP_ADMIN|GROUP_OWNER|PRIVATE_FRIEND|SUPERUSER,)
@onat.handle()#启动动态推送
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    is_group=int(isinstance(event,GroupMessageEvent))
    id=event.get_session_id()
    if not id.isdigit():
        id=id.split('_')[1]
    args = str(event.get_message()).strip()
    msg = '指令格式错误！请按照：开启全体 UID'
    if args!='' and args.isdigit():
        anchor=model.GetAnchorInfo(args)
        if len(anchor)==0:
            msg = '{} 主播不存在！请检查UID是否错误'.format(args)
        else:
            card=model.GetCard(args,id,is_group)
            if len(card)==0:
                msg='{}({})不在当前群组/私聊关注列表！'.format(anchor[1],args)
            else:
                model.AtON(args,id,is_group)
                msg='{}({})开启直播@全体成员！'.format(anchor[1],args)
    Msg=Message(msg)
    await onat.finish(Msg)

offat = on_command('关闭全体',rule=to_me(),priority=5,permission=GROUP_ADMIN|GROUP_OWNER|PRIVATE_FRIEND|SUPERUSER,)
@offat.handle()#启动动态推送
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    is_group=int(isinstance(event,GroupMessageEvent))
    id=event.get_session_id()
    if not id.isdigit():
        id=id.split('_')[1]
    args = str(event.get_message()).strip()
    msg = '指令格式错误！请按照：关闭全体 UID'
    if args!='' and args.isdigit():
        anchor=model.GetAnchorInfo(args)
        if len(anchor)==0:
            msg = '{} 主播不存在！请检查UID是否错误'.format(args)
        else:
            card=model.GetCard(args,id,is_group)
            if len(card)==0:
                msg='{}({})不在当前群组/私聊关注列表！'.format(anchor[1],args)
            else:
                model.AtOFF(args,id,is_group)
                msg='{}({})关闭直播@全体成员！'.format(anchor[1],args)
    Msg=Message(msg)
    await offat.finish(Msg)

help = on_command('帮助',rule=to_me(),priority=5,permission=GROUP_ADMIN|GROUP_OWNER|PRIVATE_FRIEND|SUPERUSER,)
@help.handle()#启动动态推送
async def handle(bot: Bot, event: MessageEvent, state: T_State):
    menu='HanayoriBot目前支持的功能：\n(请将UID替换为需操作的B站UID)\n关注 UID\n取关 UID\n列表\n开启动态 UID\n关闭动态 UID\n开启直播 UID\n关闭直播 UID\n开启全体 UID\n关闭全体 UID\n'
    info='当前版本：v0.1Beta1\n作者：鹿乃ちゃんの猫\n反馈邮箱：kano@hanayori.top'
    msg=menu+info
    Msg=Message(msg)
    await help.finish(Msg)

friend_req = on_request(priority=5)
@friend_req.handle()
async def friend_agree(bot: Bot, event: FriendRequestEvent, state: T_State):
    if str(event.user_id) in bot.config.superusers:
        await bot.set_friend_add_request(flag=event.flag, approve=True)

group_invite = on_request(priority=5)
@group_invite.handle()
async def group_agree(bot: Bot, event: GroupRequestEvent, state: T_State):
    if (event.sub_type == 'invite' and str(event.user_id) in bot.config.superusers):
        await bot.set_group_add_request(flag=event.flag, sub_type='invite',approve=True)

group_decrease = on_notice(priority=5)
@group_decrease.handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent, state: T_State):
    id=event.get_session_id()
    if not id.isdigit():
        id=id.split('_')[1]
    if event.self_id == event.user_id:
        model.DeleteGroupCard(id)