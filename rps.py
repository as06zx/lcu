import random

import members
import connect
import chat
import db

myRPS   = None
userName = None
userRPS = None
result = None
prize = None

async def resetRPS():
    global myRPS, userName, userRPS, result, prize
    myRPS   = ""
    userName = ""
    userRPS = ""
    result = ""
    prize = 0

async def takeRPS():
    global myRPS
    num = random.randint(1,3)
    if num == 1:
        myRPS = "가위"
    elif num == 2:
        myRPS = "바위"
    elif num == 3:
        myRPS = "보"

async def setUserRPS(rps):
    global userRPS
    await checkUserRPS(rps)
    userRPS = rps

async def setUserName(name):
    global userName
    userName = name

async def setUserInfo(name, rps):
    await setUserName(name)
    await setUserRPS(rps)

async def checkUserRPS(rps):
    if rps != "가위" and rps != "바위" and rps != "보":
        await chat.sendMessage(connect.lastConnection, "가위, 바위, 보 중에 한가지를 선택해주세요.")
        return

async def checkWin(rps1, rps2):
    global result  
    if rps1 == rps2:
        result = "비김"
    elif rps1 == "가위" and rps2 == "보":
        result = "패"
    elif rps1 == "바위" and rps2 == "가위":
        result = "패"
    elif rps1 == "보" and rps2 == "바위":
        result = "패"
    else:
        result = "승"

async def takePrize():
    global prize
    if result == "승":
        prize = 100
    elif result == "패":
        prize = 10
    elif result == "비김":
        prize = 50
        
async def newRPS(username, rps):
    await resetRPS()
    await takeRPS()
    await setUserInfo(username, rps)

async def startRPS():
    username = await members.getChatOwner()
    await checkWin(myRPS, userRPS)
    player = await db.findUserDB(username)
    if player:
        await takePrize()
        await db.editUserDB(username, "Point", player["Point"]+prize)
    await chat.sendMessage(connect.lastConnection, userRPS + " vs " + myRPS + " ( " + result + " ) ")

async def endRPS():
    await resetRPS()
