import time

import connect as cont
import summoner
import members
import chat
import db

commands = {}
helpMaxPage = 3

async def cmdHelp(parameter):
    connection = cont.lastConnection
    helpIndex = parameter[0]
    helpIndexIsEmpty = helpIndex == ""

    if helpIndexIsEmpty:
        helpIndex = "1"
        
    helpIndexIsNum = helpIndex.isdigit()
    outMsg = ""
    pages = f"[도움말 {helpIndex}/{helpMaxPage}"

    if not helpIndexIsNum:
        await chat.sendMessage(connection, "페이지는 숫자여야 합니다.")
        return
    if int(helpIndex) > helpMaxPage:
        await chat.sendMessage(connection, "페이지를 찾을 수 없습니다.")
        
    outMsg = outMsg + pages + "\n"
    if helpIndex == "" or helpIndex == "1":
        outMsg = outMsg + "/도움말 페이지: 도움말을 확인합니다.\n"
        outMsg = outMsg + "/인사: 인사합니다!\n"
        outMsg = outMsg + "/시간: 현재 시간을 말합니다.\n"
        outMsg = outMsg + "/인원: 방에 있는 유저수를 말합니다."
        await chat.sendMessage(connection, outMsg)
    elif helpIndex == "2":
        outMsg = outMsg + "/닉검색 닉네임: 닉네임이 사용중인지 검색합니다.\n"
        outMsg = outMsg + "/생성: 닉네임을 등록합니다.\n"
        outMsg = outMsg + "/정보 닉네임: 정보를 확인합니다.\n"
        outMsg = outMsg + "/기부 닉네임 금액: 포인트를 기부합니다."
        await chat.sendMessage(connection, outMsg)

async def cmdHi(parameter):
    connection = cont.lastConnection
    lastMessage = cont.lastEvent.data
    user = members.memberList[lastMessage["fromSummonerId"]]
    outMsg = f"{user} hi!"
    await chat.sendMessage(connection, outMsg)

async def cmdTime(parameter):
    connection = cont.lastConnection
    tm = time.localtime(time.time())
    year = str(tm.tm_year)
    mon  = str(tm.tm_mon)
    mday = str(tm.tm_mday)
    hour = str(tm.tm_hour)
    min  = str(tm.tm_min)
    outMsg = f"{year}-{mon}-{mday} | {hour}:{min}"
    await chat.sendMessage(connection, outMsg)

async def cmdMemCount(parameter):
    connection = cont.lastConnection
    memberCount = await members.getMemberCount(connection)
    outMsg = f"{str(memberCount)}명"
    await chat.sendMessage(connection, outMsg)

async def cmdFindName(parameter):
    connection = cont.lastConnection
    name = parameter[0]
    outMsg = ""
    if not await summoner.canUseUserName(connection, name):
        outMsg = "해당 닉네임은 사용중입니다."
    else:
        outMsg = "해당 닉네임은 사용중이 아닙니다."
    await chat.sendMessage(connection, outMsg)

async def cmdCreate(parameter):
    connection  = cont.lastConnection
    lastMessage = cont.lastEvent.data
    userid      = lastMessage["fromSummonerId"]
    username    = members.memberList[userid]
    
    userDB = await db.findUserDB(username)
    if userDB:
        await chat.sendMessage(connection, "이미 생성한 닉네임입니다.")
        return

    userDict = {
        "UserName" : username,
        "Level"    : 1,
        "Point"    : 1000
    }
    await db.addUserDB(userDict)
    await chat.sendMessage(connection, "생성 완료.")

async def cmdInfo(parameter):
    connection  = cont.lastConnection
    lastMessage = cont.lastEvent.data
    userid      = lastMessage["fromSummonerId"]
    username    = members.memberList[userid]
    targetName  = parameter[0]
    outMsg = ""

    targetDB = await db.findUserDB(targetName)
    if not targetDB:
        await chat.sendMessage(connection, "등록된 닉네임이 아닙니다.")
        return

    level = targetDB["Level"]
    point = targetDB["Point"]
    outMsg = outMsg + f"{targetName}'s Info\n"
    outMsg = outMsg + f"Level -> {level}\n"
    outMsg = outMsg + f"Point -> {point}"
    await chat.sendMessage(connection, outMsg)

async def cmdGive(parameter):
    if len(parameter) != 2:
        #await sendMessage(connection, "!!")
        return

    connection  = cont.lastConnection
    lastMessage = cont.lastEvent.data
    userid      = lastMessage["fromSummonerId"]
    username    = members.memberList[userid]
    targetName  = parameter[0]
    amount      = int(parameter[1])
    outMsg = ""
    
    targetDB = await db.findUserDB(targetName)
    userDB   = await db.findUserDB(username)

    if username == targetName:
        await chat.sendMessage(connection, "자신에게 보낼 수 없습니다.")
        return

    if amount > userDB["Point"]:
        await chat.sendMessage(connection, "보유중인 포인트보다 많습니다.")
        return
        
    await db.editUserDB(username,   "Point", userDB["Point"]-amount)
    await db.editUserDB(targetName, "Point", targetDB["Point"]+amount)
    outMsg = outMsg + f"{username} 포인트 기부 ({str(amount)}) -> {targetName}"
    await chat.sendMessage(connection, outMsg)
    
async def updateCommand():
    commands["?"]      = cmdHelp
    commands["help"]   = cmdHelp
    commands["도움말"] = cmdHelp
    commands["인사"]   = cmdHi
    commands["시간"]   = cmdTime
    commands["인원"]   = cmdMemCount
    commands["닉검색"] = cmdFindName
    commands["생성"]   = cmdCreate
    commands["정보"]   = cmdInfo
    commands["기부"]   = cmdGive
