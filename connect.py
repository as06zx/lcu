lastConnection = None
lastEvent      = None

async def update(connection, event):
    lastConnection = connection
    lastEvent      = event
