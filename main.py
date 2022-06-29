from lcu_driver import Connector

connector = Connector()

import re

import connect as cont
import reaction
import summoner
import members
import room
import chat
import cmd
import db
    
@connector.ready
async def connect(connection):
    await summoner.updateSummonerInfo(connection)
    await room.updateRoomInfo(connection)
    await members.updateMemberList(connection)
    await cmd.updateCommand()
    outMsg = ""
    outMsg = outMsg + "\"/도움말\"을 입력해서 명령어를 확인하세요!\n"
    outMsg = outMsg + f"현재 딜레이: {chat.delay}초"
    await chat.sendMessage(connection, outMsg)

@connector.ws.register('/lol-chat/v1/conversations/', event_types=('CREATE',))
async def onChatChanged(connection, event):
    lastMessage = event.data

    if not "body" in lastMessage:
        return

    body = lastMessage["body"]
    type = lastMessage["type"]

    await cont.update(connection, event)
    await room.updateRoomInfo(connection)
    await cmd.updateCommand()

    if type == "system" and body == "joined_room":
        await members.updateMemberList(connection)

    if type != "groupchat":
        return

    username = await members.getChatOwner()
    userDB   = await db.findUserDB(username)
    if userDB:
        await db.editUserDB(username, "Point", userDB["Point"]+1)

    if body[0:1] != "/":
        await reaction.update(username)

    if body[0:1] == "/":
        command, *parameters = body.split()
        command = command[1:]
        #print(f"{command} -> {parameters}")
        if command in cmd.commands:
            await cmd.commands[command](parameters)

@connector.close
async def disconnect(connection):
    await connector.stop()

connector.start()
