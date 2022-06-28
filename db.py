async def getUserDB():
    file = open("userdb.txt", "r")
    userDB = file.read()
    file.close()
    return userDB

async def findUserDB(username):
    file = open("userdb.txt", "r")
    flag = False
    userDB = file.readlines()
    for line in userDB:
        #print("findUserDB -> " + line)
        userData = eval(line)
        if userData['UserName'] == username:
            flag = True
            break
    file.close()
    if flag:
        return userData
    else:
        return False

async def addUserDB(userDict):
    file = open("userdb.txt", "a")
    newUser = str(userDict)
    #print("addUserDB -> " + newUser + "\n")
    file.write(newUser + "\n")
    file.close()

async def editUserDB(username, key, value):
    file = open("userdb.txt", "r")
    newUsersDB = []
    userDB = file.readlines()
    for line in userDB:
        #print("line -> " + line)
        userData = eval(line)
        if userData['UserName'] == username:
            userData[key] = value
        newUsersDB.append(userData)
        #print("newUsersDB fixed -> " + str(newUsersDB))
    file.close()
    await setUserDB(newUsersDB)
    

async def setUserDB(usersList):
    #print("setUserDB -> " + str(usersList))
    file = open("userdb.txt", "w")
    newData = ""
    for userDict in usersList:
        newData = newData + str(userDict) + "\n"
    file.write(newData)
    file.close()
