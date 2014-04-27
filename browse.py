import time
import pymongo
import random
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys


BASE_URL = 'https://imgur.com'

nativeIP = requests.get('http://icanhazip.com').text
print 'Native IP',nativeIP


# votes an image based on the image stats
def vote(driver):
    upCounter = wait.until(lambda driver:driver.find_element_by_class_name('title positive'))
    downCounter = wait.until(lambda drover:driver.find_element_by_class_name('title negative'))
    ups = int(upCounter.text)
    downs = int(upCounter.text)
    if random.randint(0,ups+downs) < ups:
        voteButton = wait.until(lambda driver:driver.find_element_by_id('mainUpArrow'))
    else:
        voteButton = wait.until(lambda driver:driver.find_element_by_id('mainDownArrow'))
    voteButton.click()


# comment based on
def comment(driver):
    print 'lol i didnt finish this'

# generates n random indices in the given size
def genIndices(size,n):
    indices = []
    for i in range(0,n):
        randomIndex = random.randint(0,size-1)
        for index in indices:
            if randomIndex >= index:
                randomIndex += 1
        indices.append(randomIndex)
        size -= 1
    return indices


########## PULL DATA FROM DATABASE ##########

# connect to database
connection = pymongo.Connection()
db = connection['imgurbotdata']
logindataCollection = db['logindata']
proxylistCollection = db['proxylist']

# get a list of user data from database
logindata = []
for account in logindataCollection.find({}):
    logindata.append(account)

# shuffle logindata
for i in range(0,len(logindata)):
    randomIndex = random.randint(i,len(logindata)-1)
    tmpLogin = logindata[i]
    logindata[i] = logindata[randomIndex]
    logindata[randomIndex] = tmpLogin

# get a list of proxies from database
proxylist = []
for proxy in proxylistCollection.find({}):
    proxylist.append(proxy)

# shuffle proxylist
for i in range(0,len(proxylist)):
    randomIndex = random.randint(i,len(proxylist)-1)
    tmpProxy = proxylist[i]
    proxylist[i] = proxylist[randomIndex]
    proxylist[randomIndex] = tmpProxy


# main loop of picking 5 accounts, logging in, browsing, and logging out
while(True):
    drivers = []
    accounts = []
    accountIndices = genIndices(len(logindata),5)
    loginStatus = [True, True, True, True, True]

    for index in accountIndices:
        accounts.append(logindata[index])


    # set up browser instances with working proxies
    for i in range(0,5):
        account = accounts[i]

        username = account['username']
        password = account['password']

        # go through the three proxies in requests until valid one is confirmed
        # if no valid proxies attached to account, select 3 new ones from the
        # proxylist collection, update the database, and repeat
        proxyNotChosen = True
        while proxyNotChosen:
            proxies = account['proxies']
            # confirm that they work. if not, regenerate ips.
            reachable = False
            attempts = 0
            nativeIP = requests.get('http://icanhazip.com').text
            while not reachable:
                # confirm proxy ip and reachability
                for proxy in proxies:
                    try:
                        print 'Trying to reach '+proxy['protocol']+'://'+proxy['ip']+':'+proxy['port']+'...'
                        testProxy = {proxy['protocol']:'http://'+proxy['ip']+':'+proxy['port']}
                        proxyIP = requests.get('http://icanhazip.com',proxies=testProxy,timeout = 4).text
                        if proxyIP != nativeIP:
                            workingProxy = proxy
                            reachable = True
                            proxyNotChosen = False
                            break
                    except:
                        attempts += 1
                        if attempts >= 100:
                            print '100 proxies failed in a row. Quitting...'
                            exit(1)

                # select new proxies
                print 'Proxies outdated. Selecting 3 new proxies for account '+username+'...'
                proxies = []
                indices = genIndices(len(proxylist),3)
                for index in indices:
                    proxies.append(proxylist[index])

            # update database with current proxies
            logindataCollection.update({'_id':account['_id']},{'$set':{'proxies':proxies}},upsert=False,multi=False)

        # selenium setup
        profile = webdriver.FirefoxProfile()
        profile.set_preference('network.proxy.type',1)
        profile.set_preference('network.proxy.http',workingProxy['ip'])
        profile.set_preference('network.proxy.http_port',workingProxy['port'])
        profile.update_preferences()
        driver = webdriver.Firefox(firefox_profile=profile)
        drivers.append(driver)
        wait = WebDriverWait(driver, 5)

        # confirm proxy ip in selenium
        drivers[i].get('http://icanhazip.com')
        try:
            seleniumIP = wait.until(lambda driver:driver.find_element_by_tag_name('pre').text)
            print 'Selenium Module IP',seleniumIP
        except:
            # try once more
            drivers[i].get('http://icanhazip.com')
            try:
                seleniumIP = wait.until(lambda driver:driver.find_element_by_tag_name('pre').text)
                print 'Selenium Module IP',seleniumIP
            except:
                print 'Selenium cannot access the proxy.'
                exit(1)

    # log in to each account
    for i in range(0,5):
        driver = drivers[i]
        driver.get(BASE_URL)
        loginButton = wait.until(lambda driver:driver.find_element_by_class_name('signin-link'))
        loginButton.click()
        usernameField = wait.until(lambda driver:driver.find_element_by_id('dd-username'))
        passwordField = wait.until(lambda driver:driver.find_element_by_id('dd-password'))
        submitButton = wait.until(lambda driver:driver.find_element_by_link_text('dd-submit'))
        usernameField.send_keys(accounts[i]['username'])
        passwordField.send_keys(accounts[i]['password'])
        submitButton.submit()
        somePost = wait.until(lambda driver:driver.find_element_by_class_name('post'))
        somePost.click()

    # simulate browsing on each user as long as one account is still logged in
    BASE_PROB = 669
    while True in loginStatus:
        for i in range(0,5):
            actionIndex = random.randint(0,1000000)
            if actionIndex < BASE_PROB:
                userButton = firefox.find_element_by_class_name('account-user-name')
                userButton.click()
                logoutButton = firefox.find_element_by_link_text('logout')
                logoutButton.click()
                drivers[i].quit()
                loginStatus[i] = False
            elif actionIndex < 6*BASE_PROB:
                vote(drivers[i])
            elif actionIndex < 10*BASE_PROB:
                comment(drivers[i])
            elif actionIndex < 180000:
                Actions.key_down(Keys.ARROW_RIGHT)
                Actions.key_up(Keys.ARROW_RIGHT)
        sleepTime = random.uniform(0,0.4)
        time.sleep(sleepTime)
