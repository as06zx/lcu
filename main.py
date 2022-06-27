from lcu_driver import Connector

connector = Connector()

import time
import re

summonerID = ''
roomID = ''
memberList = {}
commands = []

async def sendMessage(connection, text):
    global summonerID, roomID
    messageDataBody = {
    "body": "/나 " + text,
    }
    await connection.request('post', '/lol-chat/v1/conversations/' + roomID + '/messages', data=messageDataBody)
    
async def updateRoomInfo(connection):
    global roomID
    data = await (await connection.request('get', '/lol-chat/v1/conversations')).json()
    roomData = {}
    for i in data:
        if i['type'] == 'customGame':
            roomData = i
            break
    roomID = roomData['id']

async def updateMemberList(connection):
    members = (await (await connection.request('get', '/lol-lobby/v2/lobby/members/')).json())
    for dict in members:
        if not dict["summonerId"] in memberList:
            memberList[dict["summonerId"]] = dict["summonerName"]

async def getMemberCount(connection):
    members = (await (await connection.request('get', '/lol-lobby/v2/lobby/members/')).json())
    return len(members)

async def updateSummonerInfo(connection):
    global summonerID
    summoner = (await (await connection.request('get', '/lol-summoner/v1/current-summoner')).json())
    summonerID = summoner["summonerId"]

@connector.ready
async def connect(connection):
    await updateSummonerInfo(connection)
    await updateRoomInfo(connection)
    await updateMemberList(connection)
    await sendMessage(connection, "type /help for a list of commands.")

@connector.ws.register('/lol-chat/v1/conversations/', event_types=('CREATE',))
async def onChatChanged(connection, event):
    lastMessage = event.data
    body = lastMessage["body"]
    type = lastMessage["type"]

    if type != "groupchat":
        return

    if lastMessage["body"] == "/help":
        await sendMessage(connection, "reply-bot\n/hi /time /membercount")
    if lastMessage["body"] == "/hi":
        await sendMessage(connection, memberList[lastMessage["fromSummonerId"]] + " hi!")
    if lastMessage["body"] == "/time":
        tm = time.localtime(time.time())
        year = str(tm.tm_year)
        mon  = str(tm.tm_mon)
        mday = str(tm.tm_mday)
        hour = str(tm.tm_hour)
        min  = str(tm.tm_min)
        outMsg = f"{year}-{mon}-{mday} | {hour}:{min}"
        await sendMessage(connection, outMsg)
    if lastMessage["body"] == "/membercount":
        memberCount = await getMemberCount(connection)
        await sendMessage(connection, "there is " + str(memberCount) + " players")


@connector.close
async def disconnect(connection):
    await connector.stop()

connector.start()
