import random

import connect
import chat

filename = "anony.txt"

async def seeAnony():
    connection = await connect.getConnection()
    file  = open(filename, "r")
    lines = file.readlines()
    lineCount = len(lines)
    num = random.randint(0, lineCount-1)
    text = lines[num]
    await chat.sendMessage(connection, text)

async def addAnony(text):
    connection = await connect.getConnection()
    file = open(filename, "a")
    file.write(text + "\n")
    file.close()
    await chat.sendMessage(connection, "저장되었습니다.")
