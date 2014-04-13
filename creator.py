from bs4 import BeautifulSoup as soup
import sys
import pymongo
import random
import requests
import Tkinter as tk


if len(sys.argv) != 2:
    print 'Missing param: number of accounts'
    exit(1)


NUM_ACCOUNTS = int(sys.argv[1])

nounsFile = open('nouns.txt')
nouns = nounsFile.read().splitlines()
nounsFile.close()

NOUNS_SIZE = len(nouns)


class App:
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        self.button = Button(
            frame, text='QUIT', fg='red', command=frame.quit
            )
        self.button.pack(side=tk.LEFT)
        self.hi_there = Button(frame, text='Hello!', command=self.say_hi)
        self.hi_there.pack(side=tk.LEFT)

    def say_hi(self):
        print 'hi there, everyone!'

    root = tk.Tk()
    app = App(root)
    root.mainloop()
    root.destroy()


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
    # set up login details
    accountName = makeName()
    accountPassword = makePass()
    accountEmail = accountName + '@gmail.com'

    # pick 3 ips to set as primary, secondary, tertiary
    # create proxy dict, change identity to proxy

    print accountName, accountPassword, accountEmail

    #while account not created/captcha failed
        # prompt for captcha entry
        # (re)fill forms and

    # add name/password/ips to db

    created += 1


print ' -- RESULTS -- '
print created, 'accounts stored successfully to database.'
