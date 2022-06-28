lastConnection = None
lastEvent      = None

async def update(connection, event):
    lastConnection = connection
    lastEvent      = event

async def getConnection():
    return lastConnection

async def getLastMessage():
    return lastEvent.data
