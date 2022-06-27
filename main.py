from lcu_driver import Connector

connector = Connector()

import os.path
import time
import re

summonerID = ''
roomID = ''
memberList = {}
commands = {}
lastConnection = None
lastEvent = None

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

async def canUseUserName(connection, name):
    return (await (await connection.request('get', '/lol-summoner/v1/check-name-availability/' + name)).json())

async def getUserDB():
    file = open("userdb.txt", "r")
    userDB = file.read()
    file.close()
    return userDB

async def findUserDB(username):
    file = open("userdb.txt", "r")
    flag = False
    userDB = file.readlines()
    for line in userDB:
        #print("findUserDB -> " + line)
        userData = eval(line)
        if userData['UserName'] == username:
            flag = True
            break
    file.close()
    if flag:
        return userData
    else:
        return False

async def addUserDB(userDict):
    file = open("userdb.txt", "a")
    newUser = str(userDict)
    #print("addUserDB -> " + newUser + "\n")
    file.write(newUser + "\n")
    file.close()

async def editUserDB(username, key, value):
    file = open("userdb.txt", "r")
    newUsersDB = []
    userDB = file.readlines()
    for line in userDB:
        #print("line -> " + line)
        userData = eval(line)
        if userData['UserName'] == username:
            userData[key] = value
        newUsersDB.append(userData)
        #print("newUsersDB fixed -> " + str(newUsersDB))
    file.close()
    await setUserDB(newUsersDB)
    

async def setUserDB(usersList):
    #print("setUserDB -> " + str(usersList))
    file = open("userdb.txt", "w")
    newData = ""
    for userDict in usersList:
        newData = newData + str(userDict) + "\n"
    file.write(newData)
    file.close()

async def cmdHelp(parameter):
    connection = lastConnection
    helpIndex = parameter[0]
    outMsg = ""
    if helpIndex == "" or helpIndex == "1":
        outMsg = outMsg + "[help 1/2]\n/hi: ...\n/time: ...\n/membercount: ...\n"
        await sendMessage(connection, outMsg)
    elif helpIndex == "2":
        outMsg = outMsg + "[help 2/2]\n/닉검색 닉네임: 닉네임이 사용중인지 검색합니다.\n"
        outMsg = outMsg + "/생성: 닉네임을 등록합니다.\n"
        outMsg = outMsg + "/정보 닉네임: ...\n"
        await sendMessage(connection, outMsg)

async def cmdHi(parameter):
    connection = lastConnection
    lastMessage = lastEvent.data
    user = memberList[lastMessage["fromSummonerId"]]
    outMsg = f"{user} hi!"
    await sendMessage(connection, outMsg)

async def cmdTime(parameter):
    connection = lastConnection
    tm = time.localtime(time.time())
    year = str(tm.tm_year)
    mon  = str(tm.tm_mon)
    mday = str(tm.tm_mday)
    hour = str(tm.tm_hour)
    min  = str(tm.tm_min)
    outMsg = f"{year}-{mon}-{mday} | {hour}:{min}"
    await sendMessage(connection, outMsg)

async def cmdMemCount(parameter):
    connection = lastConnection
    memberCount = await getMemberCount(connection)
    outMsg = f"{str(memberCount)}명"
    await sendMessage(connection, outMsg)

async def cmdFindName(parameter):
    connection = lastConnection
    name = parameter[0]
    outMsg = ""
    if not await canUseUserName(connection, name):
        outMsg = "해당 닉네임은 사용중입니다."
    else:
        outMsg = "해당 닉네임은 사용중이 아닙니다."
    await sendMessage(connection, outMsg)

async def cmdCreate(parameter):
    connection  = lastConnection
    lastMessage = lastEvent.data
    userid      = lastMessage["fromSummonerId"]
    username    = memberList[userid]
    
    userDB = await findUserDB(username)
    if userDB:
        await sendMessage(connection, "이미 생성한 닉네임입니다.")
        return

    userDict = {
        "UserName" : username,
        "Level"    : 1,
        "Point"    : 1000
    }
    await addUserDB(userDict)
    await sendMessage(connection, "생성 완료.")

async def cmdInfo(parameter):
    connection  = lastConnection
    lastMessage = lastEvent.data
    userid      = lastMessage["fromSummonerId"]
    username    = memberList[userid]
    targetName    = parameter[0]
    outMsg = ""

    targetDB = await findUserDB(targetName)
    if not targetDB:
        await sendMessage(connection, "등록된 닉네임이 아닙니다.")
        return

    level = targetDB["Level"]
    point = targetDB["Point"]
    outMsg = outMsg + f"{targetName}'s Info\n"
    outMsg = outMsg + f"Level -> {level}\n"
    outMsg = outMsg + f"Point -> {point}"
    await sendMessage(connection, outMsg)

async def updateCommand():
    commands["help"] = cmdHelp
    commands["hi"]   = cmdHi
    commands["time"] = cmdTime
    commands["membercount"] = cmdMemCount
    commands["닉검색"] = cmdFindName
    commands["생성"]   = cmdCreate
    commands["정보"]   = cmdInfo

@connector.ready
async def connect(connection):
    await updateSummonerInfo(connection)
    await updateRoomInfo(connection)
    await updateMemberList(connection)
    await updateCommand()
    await sendMessage(connection, "type /help for a list of commands.")

@connector.ws.register('/lol-chat/v1/conversations/', event_types=('CREATE',))
async def onChatChanged(connection, event):
    global lastConnection, lastEvent
    lastMessage = event.data
    body = lastMessage["body"]
    type = lastMessage["type"]
    lastConnection = connection
    lastEvent = event

    if type != "groupchat":
        return

    if body[0:1] == "/":
        command = (body[1:]).split(" ", 1)[0]
        parameters = re.split('\s+', body[len(command)+1:len(body)].strip())
        if command in commands:
            await commands[command](parameters)

@connector.close
async def disconnect(connection):
    await connector.stop()

connector.start()
