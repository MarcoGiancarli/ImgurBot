import os
import sys
import pymongo
import random

if len(sys.argv) != 2:
    print 'Missing param: number of accounts'
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


created = 0 # number of accounts added to DB

while created < NUM_ACCOUNTS:
    accountName = makeName()
    accountPassword = makePass()
    accountEmail = accountName + '@gmail.com'

    print accountName, accountPassword, accountEmail

    #while account not created/captcha failed
        #captchaText = os.popen('OCR.java IMAGENAMEFUCKSHIT')
        #fill forms + captcha

    # add name/password to db

    created += 1


print ' -- RESULTS -- '
print created, 'accounts stored successfully to database.'
