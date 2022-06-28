memberList = {}

async def updateMemberList(connection):
    members = (await (await connection.request('get', '/lol-lobby/v2/lobby/members/')).json())
    for dict in members:
        if not dict["summonerId"] in memberList:
            memberList[dict["summonerId"]] = dict["summonerName"]

async def getMemberCount(connection):
    members = (await (await connection.request('get', '/lol-lobby/v2/lobby/members/')).json())
    return len(members)
