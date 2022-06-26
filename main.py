from lcu_driver import Connector

connector = Connector()

summonerID = ''
roomID = ''
memberList = {}

async def sendMessage(connection, text):
    global summonerID, roomID
    messageDataBody = {
    "body": "[a] " + text,
    "fromId": roomID,
    "fromPid": roomID ,
    "fromSummonerId": int(summonerID),
    "id": "1655714801452:63", # what is this???
    "isHistorical": True,
    "timestamp": "2022-06-20T08:46:41.560Z", # u-u;;;
    "type": "chat"
    }
    
    await connection.request('post', '/lol-chat/v1/conversations/' + roomID + '/messages', data=messageDataBody)
    

@connector.ready
async def connect(connection):
    global summonerID, roomID, memberList
    print('LCU API is ready to be used.')
    summoner = (await (await connection.request('get', '/lol-summoner/v1/current-summoner')).json())
    summonerID = summoner['summonerId']
    #print(summoner)

    roomData = (await (await connection.request('get', '/lol-chat/v1/conversations')).json())[1]
    roomID = roomData['id']
    #print(roomData)
    
    roomMessages =(await (await connection.request('get', '/lol-chat/v1/conversations/' + roomID + "/messages")).json())[1]
    #print(roomMessages)

    #await sendMessage(connection, "hi py!")
    #print(await test.json())
    # but it works without change!

    members = (await (await connection.request('get', '/lol-lobby/v2/lobby/members/')).json())

    for dict in members:
        memberList[dict["summonerId"]] = dict["summonerName"]

    await sendMessage(connection, "type /help for a list of commands.")

@connector.ws.register('/lol-chat/v1/conversations/', event_types=('CREATE',))
async def onChatChanged(connection, event):

    lastMessage = event.data

    #print(lastMessage)

    if lastMessage["body"] == "/help":
        await sendMessage(connection, "/hi: say hi\n/time: say time")
    if lastMessage["body"] == "/hi":
        await sendMessage(connection, memberList[lastMessage["fromSummonerId"]] + " hi!")
    if lastMessage["body"] == "/time":
        await sendMessage(connection, lastMessage["timestamp"])


@connector.close
async def disconnect(connection):
    print('Finished task')
    await connector.stop()

connector.start()