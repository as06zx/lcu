import asyncio
import random
import time

import members
import connect
import chat
import db

player = None
maxTime = None
startTime    = None
waitingTime  = None
reactionTime = None
testIsStarted    = None
testIsInProgress = None
testIsSuccess    = None

async def resetData():
    global player, maxTime, startTime, waitingTime, reactionTime, testIsStarted, testIsInProgress, testIsSuccess
    player = ""
    maxTime      = 0
    startTime    = 0
    waitingTime  = 0
    reactionTime = 0
    testIsStarted    = False
    testIsInProgress = False
    testIsSuccess    = False

async def checkIfStarted():
    return testIsStarted

async def checkIfProgress():
    return testIsInProgress

async def setUserName(name):
    global player
    player = name

async def setSuccess(bool):
    global testIsSuccess
    testIsSuccess = bool

async def setStartTime(value):
    global startTime
    startTime = value

async def setWaitingTime(value):
    global waitingTime
    waitingTime = value

async def setMaxTime(value):
    global maxTime
    maxTime = value

async def setIsInProgress(bool):
    global testIsInProgress
    testIsInProgress = bool

async def setReactionTime(value):
    global reactionTime
    reactionTime = value

async def setStarted(bool):
    global testIsStarted
    testIsStarted = bool

async def getUserName():
    return player

async def getMaxTime():
    return maxTime

async def getStartTime():
    return startTime

async def getWaitingTime():
    return waitingTime

async def startTest():
    connection = await connect.getConnection()
    await chat.sendMessage(connection, "!!!!!", True)
    await setStarted(True)
    await checkTimeOver()

async def start():
    print("reaction.start")
    connection = await connect.getConnection()
    await chat.sendMessage(connection, "느낌표가 올라오면 채팅을 쳐주세요!") 
    await setStartTime(time.time())
    await setWaitingTime(random.randint(3, 9))
    await setMaxTime(waitingTime * 2)
    await setIsInProgress(True)
    await waiting()

async def waiting():
    while testIsInProgress:
        await asyncio.sleep(0.001)
        #time.sleep(0.001)
        currentTime = time.time()
        if currentTime-waitingTime > startTime:
            await startTest()
            break

async def newTest(username):
    await resetData()
    await setUserName(username)

async def checkIsSuccess():
    print("reaction.checkIsSuccess " + str(testIsSuccess))
    if testIsSuccess:
        username = await members.getChatOwner()
        userDB   = await db.findUserDB(username)
        if userDB:
            await db.editUserDB(username, "Point", userDB["Point"]+50)

async def testEnd():
    await checkIsSuccess()
    await resetData()
    
async def playerDidChat():
    print("reaction.playerDidChat")
    connection = await connect.getConnection()
    currentTime  = time.time()
    await setReactionTime(currentTime - startTime - waitingTime)
    await setSuccess(True)
    outMsg = f"반응속도 -> {reactionTime}"
    await chat.sendMessage(connection, outMsg)
    await testEnd()

async def tooSoon():
    print("reaction.tooSoon")
    connection = await connect.getConnection()
    await setSuccess(False)
    await chat.sendMessage(connection, "너무 빠릅니다!")
    await testEnd()

async def checkTestResult():
    if (await checkIfStarted()):
        await playerDidChat()
    else:
        await tooSoon()

async def timeOver():
    print("reaction.timeOver")
    connection = await connect.getConnection()
    await setSuccess(False)
    await chat.sendMessage(connection, "입력이 없어 테스트가 종료되었습니다.")
    await testEnd()

async def checkDidChat(username):
    playerName = await getUserName()
    if username == playerName:
        await checkTestResult()
        return True
    return False

async def checkTimeOver():
    while True:
        await asyncio.sleep(0.001)
        #time.sleep(0.001)
        tm = time.time()
        maxTime   = await getMaxTime()
        startTime = await getStartTime()
        if tm-maxTime > startTime:
            await timeOver()
            break

async def update(username):
    if (await checkIfProgress()):
        await checkDidChat(username)
