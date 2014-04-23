import sys
import pymongo
from bs4 import BeautifulSoup as soup
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import *
import random

if len(sys.argv) != 4:
    print 'Invalid params! Usage: <image key> <number of votes> <up/down>'
    exit(1)


LOGIN_URL = 'https://imgur.com/signin'
IMAGE_URL = 'https://imgur.com/' + sys.argv[1]
NUM_VOTES = int(sys.argv[2])
voteCount = 0

if sys.argv[3] == 'up':
    vote = True
elif sys.argv[3] == 'down':
    vote = False
else:
    print 'You need to specify "up" or "down" for the third param.'
    exit(1)

nativeIP = requests.get('http://icanhazip.com').text
print 'Native IP',nativeIP


# generates 3 random indices in the given size
def genIndices(size):
    indices = []
    for i in range(0,3):
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


# cycle through the shuffled account list
for account in logindata:
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
            proxies = []
            indices = genIndices(len(proxylist))
            for index in indices:
                proxies.append(proxylist[index])

    # update database with current proxies
    logindataCollection.update({'_id':account['_id']},{'$set':{'proxies':proxies}},upsert=False,multi=False)


    ########## BEGIN SELENIUM ##########

    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.proxy.type',1)
    profile.set_preference('network.proxy.http',workingProxy['ip'])
    profile.set_preference('network.proxy.http_port',workingProxy['port'])
    profile.update_preferences()
    firefox = webdriver.Firefox(firefox_profile=profile)
    wait = WebDriverWait(firefox, 5)

    # confirm proxy ip in selenium
    firefox.get('http://icanhazip.com')
    try:
        seleniumIP = wait.until(lambda firefox:firefox.find_element_by_tag_name('pre').text)
        print 'Selenium Module IP',seleniumIP
    except:
        # try once more
        firefox.get('http://icanhazip.com')
        try:
            seleniumIP = wait.until(lambda firefox:firefox.find_element_by_tag_name('pre').text)
            print 'Selenium Module IP',seleniumIP
        except:
            print 'Selenium cannot access the proxy.'

    # imgur login page
    firefox.get(LOGIN_URL)
    # get fields
    userField = wait.until(lambda firefox:firefox.find_element_by_name('username'))
    passField = wait.until(lambda firefox:firefox.find_element_by_name('password'))
    submitButton = wait.until(lambda firefox:firefox.find_element_by_name('submit'))
    # fill forms and submit
    userField.send_keys(username)
    passField.send_keys(password)
    submitButton.submit()

    # go to image url and upvote! <insert upvote gif here>
    firefox.get(IMAGE_URL)
    if vote:
        voteButton = wait.until(lambda firefox:firefox.find_element_by_id('mainUpArrow'))
        if 'pushed' not in voteButton.get_attribute('class'):
            voteButton.click()
    else:
        voteButton = wait.until(lambda firefox:firefox.find_element_by_id('mainDownArrow'))
        if 'pushed' not in voteButton.get_attribute('class'):
            voteButton.click()
    voteCount += 1

    # log out of imgur
    userButton = firefox.find_element_by_class_name('account-user-name')
    userButton.click()
    logoutButton = firefox.find_element_by_link_text('logout')
    logoutButton.click()
    firefox.quit()

    # break if we have enough votes.
    if voteCount >= NUM_VOTES:
        break

########## RESULTS ##########

if vote == True:
    print 'Successful upvotes:', voteCount
if vote == False:
    print 'Successful downvotes:', voteCount
