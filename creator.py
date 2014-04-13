import os
import sys
import pymongo
import random

if len(sys.argv) != 2:
    print 'Missing param: number of accounts'
    exit(1)

NUM_ACCOUNTS = sys.argv[1]

nounsFile = open('nouns.txt')
nouns = nounsFile.read().splitlines()
nounsFile.close()

NOUNS_SIZE = len(nouns)


def makeName():
    accountName = ''

    # first word
    randomIndex = random.randint(0,NOUNS_SIZE)
    accountName += nouns[randomIndex]

    # second word
    randomIndex = random.randint(0,NOUNS_SIZE)
    accountName += nouns[randomIndex]

    # number
    randomIndex = random.randint(1,999)
    accountName += str(randomIndex)

    return accountName


def makePass():
    accountPassword = ''

    # add word
    randomIndex = random.randint(0,NOUNS_SIZE)
    accountPassword += nouns[randomIndex]

    # add number
    randomIndex = random.randint(1,999)
    accountPassword += str(randomIndex)

    return accountPassword


created = 0 # number of accounts added to DB

while created < NUM_ACCOUNTS:
    accountName = makeName()
    accountPassword = makePass()
    accountEmail = accountName + '@gmail.com'
    print accountName, accountPassword, accountEmail
    #captchaText = os.popen('OCR.java IMAGENAMEFUCKSHIT')

    # add name/password to db
