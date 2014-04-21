import sys
import pymongo
import random
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import *

if len(sys.argv) != 2:
    print 'Missing param! Usage: creator.py <number of accounts>'
    exit(1)

nounsFile = open('nouns.txt')
nouns = nounsFile.read().splitlines()
nounsFile.close()

NUM_ACCOUNTS = int(sys.argv[1])
NOUNS_SIZE = len(nouns)
REGISTER_URL = 'https://imgur.com/register'


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


connection = pymongo.Connection()
db = connection['imgurbotdata']
logindata = db['logindata']
proxyCollection = db['proxylist'].find({})

# check logindata size
numAccountsInDB = 0
accountList = logindata.find({})
for account in accountList:
    numAccountsInDB += 1

# throw proxy collection into a list for easy access
proxylist = []
for proxy in proxyCollection:
    proxylist.append(proxy)

# shuffle proxylist
for i in range(0,len(proxylist)):
    randomIndex = random.randint(i,len(proxylist)-1)
    tmp = proxylist[i]
    proxylist[i] = proxylist[randomIndex]
    proxylist[randomIndex] = tmp


numCreated = 0 # number of accounts added to database

while numCreated < NUM_ACCOUNTS:

    # set up login details
    accountName = makeName()
    accountPassword = makePass()
    accountEmail = accountName + '@gmail.com'

    # pick 3 random ips to set as primary, secondary, tertiary.
    # confirm that they work. if not, regenerate ips.
    reachable = False
    attempts = 0
    nativeIP = requests.get('http://icanhazip.com').text
    while not reachable:
        proxies = []
        indices = genIndices(len(proxylist))
        for index in indices:
            proxies.append(proxylist[index])

        # confirm proxy ip and reachability
        for proxy in proxies:
            try:
                print 'Trying to reach '+proxy['protocol']+'://'+proxy['ip']+':'+proxy['port']+'...'
                testProxy = {proxy['protocol']:'http://'+proxy['ip']+':'+proxy['port']}
                proxyIP = requests.get('http://icanhazip.com',proxies=testProxy,timeout = 5).text
                if proxyIP != nativeIP:
                    workingProxy = proxy
                    reachable = True
                    break
            except:
                attempts += 1
                if attempts >= 100:
                    print '100 proxies failed in a row. Quitting...'
                    exit(1)

    print 'Attempting to create:',accountName,'--',accountPassword+'...'


    ########## BEGIN SELENIUM ##########

    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.proxy.type',1)
    profile.set_preference('network.proxy.http',workingProxy['ip'])
    profile.set_preference('network.proxy.http_port',workingProxy['port'])
    profile.update_preferences()
    firefox = webdriver.Firefox(firefox_profile=profile)
    wait = WebDriverWait(firefox, 8)

    # confirm proxy ip in selenium
    firefox.get('http://icanhazip.com')
    try:
        seleniumIP = wait.until(lambda firefox:firefox.find_element_by_tag_name('pre').text)
    except:
        # try once more
        firefox.get('http://icanhazip.com')
        try:
            seleniumIP = wait.until(lambda firefox:firefox.find_element_by_tag_name('pre').text)
        except:
            print 'Selenium cannot reach the proxy. Now quitting...'
            exit(1)

    if seleniumIP == nativeIP:
        print 'Selenium\'s IP matches the native IP! Now quitting...'
        exit(1)
    else:
        print 'Selenium has reached the proxy! Beginning registration...'

    # Captcha time. repeat until correct.
    correct = False
    while not correct:
        firefox.get(REGISTER_URL)

        nameForm = wait.until(lambda firefox:firefox.find_element_by_id('url'))
        emailForm = wait.until(lambda firefox:firefox.find_element_by_id('email'))
        passForm = wait.until(lambda firefox:firefox.find_element_by_id('password'))
        confirmForm = wait.until(lambda firefox:firefox.find_element_by_id('confirmPassword'))
        captchaForm = wait.until(lambda firefox:firefox.find_element_by_id('recaptcha_response_field'))
        agreeBox = wait.until(lambda firefox:firefox.find_element_by_id('agree'))

        nameForm.send_keys(accountName)
        emailForm.send_keys(accountEmail)
        passForm.send_keys(accountPassword)
        confirmForm.send_keys(accountPassword)
        agreeBox.click()
        captchaForm.click()

        # wait for user response before continuing!
        # when we see either of these two elements, we have succeeded or failed
        while True:
            try:
                nextPage = wait.until(lambda firefox:firefox.find_element_by_class_name(
                        'total-images-suffix'))
                print 'Captcha entered correctly. Would you like a cookie, or a gold star?'
                correct = True    # if we get this far, everything is good
                break
            except:
                pass
            try:
                failCheck = wait.until(lambda firefox:firefox.find_element_by_class_name(
                        'textbox explanation error center'))
                print 'You failed the captcha. YOU HAD ONE JOB. Retrying...'
                break
            except:
                pass

    # Nailed it.

    # logout now, we're done creating this account
    userButton = firefox.find_element_by_class_name('account-user-name')
    userButton.click()
    logoutButton = firefox.find_element_by_link_text('logout')
    logoutButton.click()

    # add name/password/ips to db if creation was successful
    logindata.insert({'username':accountName,'password':accountPassword,'proxies':proxies})

    numCreated += 1
    print 'Successfully created:',accountName,'--',accountPassword+'.'
    print 'Created',numCreated,'of',NUM_ACCOUNTS,'so far.'
    firefox.quit()


print ' -- RESULTS -- '
print numCreated, 'accounts stored successfully to database.'
print 'Total accounts in database:', numCreated + numAccountsInDB
