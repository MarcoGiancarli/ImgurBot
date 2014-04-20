from bs4 import BeautifulSoup as soup
import sys
import pymongo
import random
import requests

if len(sys.argv) != 2:
    print 'Missing param! Usage: creator.py <number of accounts>'
    exit(1)

NUM_ACCOUNTS = int(sys.argv[1])

nounsFile = open('nouns.txt')
nouns = nounsFile.read().splitlines()
nounsFile.close()

NOUNS_SIZE = len(nouns)


def makeName():
    accountName = ''
    # first word
    randomIndex = random.randint(1,NOUNS_SIZE) - 1
    accountName += nouns[randomIndex]
    # second word
    randomIndex = random.randint(1,NOUNS_SIZE) - 1
    accountName += nouns[randomIndex]
    # number
    randomIndex = random.randint(1,999)
    accountName += str(randomIndex)
    return accountName


def makePass():
    accountPassword = ''
    # add word
    randomIndex = random.randint(1,NOUNS_SIZE) - 1
    accountPassword += nouns[randomIndex]
    # add number
    randomIndex = random.randint(1,999)
    accountPassword += str(randomIndex)
    return accountPassword

connection = pymongo.Connection()
db = connection['imgurbotdata']
logindata = db['logindata']
proxies = db['proxylist'].find()

proxylist = []
while proxies.hasNext()
    proxy = proxies.next()
    proxylist.add(proxy)

print proxylist

numCreated = 0 # number of accounts added to database

while numCreated < NUM_ACCOUNTS:
    # set up login details
    accountName = makeName()
    accountPassword = makePass()
    accountEmail = accountName + '@gmail.com'

    # pick 3 ips to set as primary, secondary, tertiary

    print accountName, accountPassword, accountEmail

    #while account not created/captcha failed
        # prompt for captcha entry
        # (re)fill forms and

    # add name/password/ips to db
    logindata.insert

    numCreated += 1


print ' -- RESULTS -- '
print numCreated, 'accounts stored successfully to database.'
