import room

async def sendMessage(connection, text):
    print(room.roomID)
    messageDataBody = {
    "body": "/나 " + text,
    }
    await connection.request('post', '/lol-chat/v1/conversations/' + room.roomID + '/messages', data=messageDataBody)

