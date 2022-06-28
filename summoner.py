summonerID = ''

async def updateSummonerInfo(connection):
    global summonerID
    summoner = (await (await connection.request('get', '/lol-summoner/v1/current-summoner')).json())
    summonerID = summoner["summonerId"]

async def canUseUserName(connection, name):
    return (await (await connection.request('get', '/lol-summoner/v1/check-name-availability/' + name)).json())
