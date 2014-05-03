import sys
import requests
from imgurbot import *

if len(sys.argv) != 2:
    print 'Missing param! Usage: creator.py <number of accounts>'
    exit(1)

NUM_TO_CREATE = int(sys.argv[1])
num_created = 0
db = Database()
db.shuffle_proxies()

print 'Number of accounts in database: ' + str(db.login_count)
print 'Number of proxies in database:  ' + str(db.proxy_count)
print '-'*40

while num_created < NUM_TO_CREATE:

    # set up login details
    username = db.make_name()
    password = db.make_pass()

    # get proxies in sets of 3. get an active one. if none work, get 3 more.
    no_active_proxy = True
    attempts = 0
    while no_active_proxy:
        indices = db.make_indices(db.proxy_count, 3)
        proxies = [db.proxylist[i] for i in indices]
        for proxy in proxies:
            if db.test_proxy(proxy):
                active_proxy = proxy
                no_active_proxy = False
                break
        attempts += 1
        if attempts>30:
            print 'Failed to reach too many proxies. Try updating your proxies. Shutting down.'
            exit(1)

    print 'Attempting to create: '+username+' -- '+password+'...'

    try:
        bot = Imgurbot(active_proxy)
        bot.create(username, password)
        db.add_login(username, password, proxies)
        print 'Successfully created: '+username+' -- '+password+'.'
        print 'Created '+str(num_created)+' of '+str(NUM_TO_CREATE)+' so far. '+str(db.login_count)+' in total.'
        num_created += 1
        bot.logout()
        bot.driver.quit()
    except BadProxyError:
        bot.driver.quit()
        print 'Selenium can\'t reach the proxy. Making another account...'
        print 'BAD PROXY ERROR: The apparent IP when accessing the web is incorrect.'
    except CantReachProxyError:
        bot.driver.quit()
        print 'Selenium can\'t reach the proxy. Making another account...'
        print 'CANT REACH PROXY ERROR: Proxy seems to be offline.'
    except CantFindElementError:
        bot.driver.quit()
        print 'Selenium has encountered a problem: the HTTPS proxy has failed and is no longer accessible.'
        print 'Account created successfully, but failed to exit normally.'


print '-'*40
print 'RESULTS:'
print num_created, 'accounts stored successfully to database.'
print 'Total accounts in database:', db.login_count
