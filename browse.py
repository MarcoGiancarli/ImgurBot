import sys
import time
import random
from imgurbot import *


db = Database()
db.shuffle_logins()


# main loop of picking 5 accounts, logging in, browsing, and logging out
while(True):
    account = db.next_login()
    try:
        print 'Trying to log in on user',account['username'],'('+account['username']+')...'
        active_proxy = db.fix_proxies(account)
        bot = Imgurbot(active_proxy)
        bot.login(account['username'], account['password'])
        bot.nav_to_gallery()
        print 'Logged in as user',account['username']
    except:
        print 'Failed to log in to user',account['username']

    # simulate browsing on the user as long as it is still logged in
    login_status = True
    BASE_PROB = 750
    while login_status:
        action_index = random.randint(0,1000000)
        if action_index < BASE_PROB:
            try:
                sys.stdout.write('Attempting to log out of account...')
                sys.stdout.flush()
                bot.logout()
                login_status = False
            except:
                print ' FAILED'
        elif action_index < 6 * BASE_PROB:
            try:
                sys.stdout.write('Attempting to comment on the current post...')
                sys.stdout.flush()
                bot.comment('lolwut')
                print ' SUCCESS'
            except:
                print ' FAILED'
        elif action_index < 10 * BASE_PROB:
            try:
                sys.stdout.write('Attempting to vote on the current post...')
                sys.stdout.flush()
                bot.auto_vote()
                print ' SUCCESS'
            except:
                print ' FAILED'
        elif action_index < 300 * BASE_PROB:
            try:
                print 'Next.'
                bot.go_to_next()
            except:
                print 'Could\'nt find the "next" button.'
        sleepTime = random.uniform(0.5,1.9)
        time.sleep(sleepTime)
