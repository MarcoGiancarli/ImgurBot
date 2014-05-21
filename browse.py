import sys
import time
import random
from imgurbot import *


db = Database()


for account in db.next_login():
    try:
        print 'Trying to log in on user',account['username'],'('+account['password']+')...'
        active_proxy = db.fix_proxies(account)
        bot = Imgurbot(active_proxy)
        bot.login(account['username'], account['password'])
        bot.nav_to_usersub()
        print 'Logged in as user',account['username']
    except:
        print 'Failed to log in to user',account['username']

    # simulate browsing on the user as long as it is still logged in
    login_status = True
    fail_count = 0
    BASE_PROB = 500
    while login_status:
        action_index = random.randint(0,400000)
        if action_index < BASE_PROB or fail_count > 5:
            try:
                sys.stdout.write('Attempting to log out of account...')
                sys.stdout.flush()
                bot.logout()
                bot.driver.quit()
                login_status = False
                print ' SUCCESS'
                fail_count = 0
            except:
                print ' FAILED'
                fail_count += 1
        elif action_index < 6 * BASE_PROB:
            try:
                sys.stdout.write('Attempting to comment on the current post...')
                sys.stdout.flush()
                bot.comment(db.viralize())
                print ' SUCCESS'
                fail_count = 0
            except:
                print ' FAILED'
                fail_count += 1
        elif action_index < 10 * BASE_PROB:
            try:
                sys.stdout.write('Attempting to vote on the current post...')
                sys.stdout.flush()
                bot.auto_vote()
                print ' SUCCESS'
                fail_count = 0
            except:
                print ' FAILED'
                fail_count += 1
        elif action_index < 125 * BASE_PROB:
            try:
                print 'Next.'
                bot.go_to_next()
                fail_count = 0
            except:
                print 'Could\'nt find the "next" button.'
                fail_count += 1
        sleepTime = random.uniform(0.9,4.5)
        time.sleep(sleepTime)
