import sys
import pymongo
from bs4 import BeautifulSoup as soup
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import *

if len(sys.argv) != 4:
    print 'Invalid params! Usage: <image key> <number of votes> <up/down>'
    exit(1)


LOGIN_URL = 'https://imgur.com/signin'
IMAGE_URL = 'https://imgur.com/' + sys.argv[1]
numVotes = int(sys.argv[2])
voteCount = 0

if sys.argv[3] == 'up':
    vote = True
elif sys.argv[3] == 'down':
    vote = False
else:
    print 'You need to specify "up" or "down" for the third param.'
    exit(1)

########## GET PROXY/USER/PASS FROM DB ##########

# go through list of proxies until valid one is confirmed
# if no valid proxies attached to account, select 3 new ones

username = 'decisions'
password = '052795'
nativeIP = requests.get('http://icanhazip.com').text
proxies = {'http':'http://221.176.14.72:80'}
requestsIP = requests.get('http://icanhazip.com',proxies=proxies).text
print 'Native IP',nativeIP
print 'Requests Module IP',requestsIP

########## BEGIN SELENIUM ##########

profile = webdriver.FirefoxProfile()
profile.set_preference('network.proxy.type',1)
profile.set_preference('network.proxy.http','24.96.4.198')
profile.set_preference('network.proxy.http_port',8080)
profile.update_preferences()
firefox = webdriver.Firefox(firefox_profile=profile)
wait = WebDriverWait(firefox, 5)

# confirm proxy ip
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
userField = firefox.find_element_by_name('username')
passField = firefox.find_element_by_name('password')
submitButton = firefox.find_element_by_name('submit')
# fill forms and submit
userField.send_keys(username)
passField.send_keys(password)
submitButton.submit()
# go to image url and upvote! <insert upvote gif here>
firefox.get(IMAGE_URL)
if vote:
    voteButton = firefox.find_element_by_id('mainUpArrow')
else:
    voteButton = firefox.find_element_by_id('mainDownArrow')
voteButton.click()
voteCount += 1
# log out of imgur
userButton = firefox.find_element_by_class_name('account-user-name')
userButton.click()
logoutButton = firefox.find_element_by_link_text('logout')
logoutButton.click()
firefox.quit()

########## RESULTS ##########

if vote == True:
    print 'Successful upvotes:', voteCount
if vote == False:
    print 'Successful downvotes:', voteCount
