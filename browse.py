import sys
import time
import random
from imgurbot import *


db = Database()
db.shuffle_logins


# main loop of picking 5 accounts, logging in, browsing, and logging out
while(True):
    account = db.next_login()
    try:
        print 'Trying to log in on user',account['username'],'('+account['username']+')...'
        active_proxy = db.fix_proxies(account)
        bot = Imgurbot(active_proxy)
        bot.login(account['username'], account['password'])
        bot.nav_to_gallery()
    except:
        print 'Failed to log in to user',account['username']

    # simulate browsing on the user as long as it is still logged in
    login_status = True
    BASE_PROB = 669
    while login_status:
        action_index = random.randint(0,2000000)
        #try:
        if action_index < BASE_PROB:
            sys.stdout.write('Logging out of account...')
            sys.stdout.flush()
            bot.logout()
            print ' FAILED'
            login_status = False
        elif action_index < 6 * BASE_PROB:
            sys.stdout.write('Attempting to comment on the current post...')
            sys.stdout.flush()
            bot.comment('lolwut')
            print ' FAILED'
        elif action_index < 10 * BASE_PROB:
            sys.stdout.write('Attempting to vote on the current post...')
            sys.stdout.flush()
            bot.auto_vote()
            print ' SUCCESS'
        elif action_index < 300 * BASE_PROB:
            bot.go_to_next()
        #except:
            #print 'Failed to perform action.'
        sleepTime = random.uniform(0,1.9)
        time.sleep(sleepTime)
