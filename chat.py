import time

import room

lastTimeSent = 0
delay = 2 # for prevent spam, i make delay for it.

async def sendMessage(connection, text):
    global lastTimeSent
    if not (await checkDelay()):
        return
    lastTimeSent = time.time()
    messageDataBody = {
    "body": "/나 " + text,
    }
    await connection.request('post', '/lol-chat/v1/conversations/' + room.roomID + '/messages', data=messageDataBody)

async def checkDelay():
    tm = time.time()
    if tm-delay > lastTimeSent:
        return True
    else:
        return False
