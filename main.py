from lcu_driver import Connector

connector = Connector()

import os.path
import time
import re

import connect as cont
import summoner
import members
import room
import chat
import cmd
import db

lastEvent = None
    
@connector.ready
async def connect(connection):
    await summoner.updateSummonerInfo(connection)
    await room.updateRoomInfo(connection)
    await members.updateMemberList(connection)
    await cmd.updateCommand()
    await chat.sendMessage(connection, "type /help for a list of commands.")

@connector.ws.register('/lol-chat/v1/conversations/', event_types=('CREATE',))
async def onChatChanged(connection, event):
    global lastEvent
    lastMessage = event.data

    if not "body" in lastMessage:
        return

    body = lastMessage["body"]
    type = lastMessage["type"]
    cont.lastConnection = connection
    cont.lastEvent = event

    if type != "groupchat":
        return

    userid      =   lastMessage["fromSummonerId"]
    username    =   members.memberList[userid]    
    userDB      =   await db.findUserDB(username)
    if userDB:
        await db.editUserDB(username, "Point", userDB["Point"]+1)

    # move to here ->  userinfo -> later u-u
    if body[0:1] == "/":
        command = (body[1:]).split(" ", 1)[0]
        parameters = re.split('\s+', body[len(command)+1:len(body)].strip())
        if command in cmd.commands:
            await cmd.commands[command](parameters)

@connector.close
async def disconnect(connection):
    await connector.stop()

connector.start()
