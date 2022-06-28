import connect

memberList = {}

async def updateMemberList(connection):
    members = (await (await connection.request('get', '/lol-lobby/v2/lobby/members/')).json())
    for dict in members:
        if not dict["summonerId"] in memberList:
            memberList[dict["summonerId"]] = dict["summonerName"]

async def getMemberCount(connection):
    members = (await (await connection.request('get', '/lol-lobby/v2/lobby/members/')).json())
    return len(members)

async def checkMemberIsNone(key):
    if not key in memberList:
        return True
    else:
        return False

async def getMemberName(id):
    if not (await checkMemberIsNone(id)):
        return memberList[id]

async def getChatOwner():
    userid = (await connect.getLastMessage())["fromSummonerId"]
    return memberList[userid]
