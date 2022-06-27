from lcu_driver import Connector

connector = Connector()

summonerID = ''
roomID = ''
memberList = {}

async def sendMessage(connection, text):
    global summonerID, roomID
    messageDataBody = {
    "body": "/나 " + text,
    "fromId": roomID,
    "fromPid": roomID ,
    "fromSummonerId": int(summonerID),
    "id": "1655714801452:63",
    "isHistorical": True,
    "timestamp": "2022-06-20T08:46:41.560Z",
    "type": "chat"
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

    if lastMessage["body"] == "/help":
        await sendMessage(connection, "reply-bot\n/hi: say hi\n/time: say time")
    if lastMessage["body"] == "/hi":
        await sendMessage(connection, memberList[lastMessage["fromSummonerId"]] + " hi!")
    if lastMessage["body"] == "/time":
        await sendMessage(connection, lastMessage["timestamp"])


@connector.close
async def disconnect(connection):
    await connector.stop()

connector.start()
