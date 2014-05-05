from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import *
from pymongo import Connection
import requests
import random
import sys


# In case selenium can't reach the proxy
class CantReachProxyError(Exception):
    def __init__(self, proxy):
        self.driver.quit()
        self.proxy = proxy


# In case selenium can reach the proxy, but the IP is wrong
class BadProxyError(Exception):
    def __init__(self, proxy):
        self.driver.quit()
        self.proxy = proxy


# If for any reason we find ourselves at the wrong page
class CantFindLinkError(Exception):
    def __init__(self, url, link_text):
        self.url = url
        self.link_text = link_text
    def __str__(self):
        return '"' + self.link_text + '" at page: ' + self.url


# In case the page we're on doesn't have the elements we're looking for
class CantFindElementError(Exception):
    def __init__(self, url, element):
        self.url = url
        self.element = element
    def __str__(self):
        return self.element + ' at page: ' + self.url


# This class will handle most of the automation in selenium.
class Imgurbot:
    def __init__(self, proxy):
        self.proxy = proxy

        # set up new driver
        proxies = Proxy({proxy['protocol']+'Proxy':proxy['ip']+':'+proxy['port'],
                         'httpProxy'              :proxy['ip']+':'+proxy['port']})
        self.driver = webdriver.Firefox(proxy=proxies)
        self.wait8s = WebDriverWait(self.driver, 8)
        self.wait1s = WebDriverWait(self.driver, 1)

        # confirm proxy ip in selenium
        confirmed = False
        for attempt in xrange(1,4):
            try:
                self.driver.get('http://icanhazip.com')
                seleniumIP = self.wait8s.until(lambda driver:driver.find_element_by_tag_name('pre').text)
                confirmed = True
                break
            except:
                print 'Selenium proxy confirmation attempt '+str(attempt)+' failed.'

        if not confirmed:
            raise CantReachProxyError(proxy)
        if seleniumIP == self.proxy['ip']:
            print 'Selenium has reached the proxy at IP ' + seleniumIP + '...'
        else:
            raise BadProxyError(proxy)


    def create(self, username, password):
        REGISTER_URL = 'https://imgur.com/register'

        correct = False
        while not correct:
            self.driver.get(REGISTER_URL)
            forms_found = False
            while not forms_found:
                try:
                    name_form    = self.wait1s.until(lambda driver:driver.find_element_by_id('url'))
                    email_form   = self.wait1s.until(lambda driver:driver.find_element_by_id('email'))
                    pass_form    = self.wait1s.until(lambda driver:driver.find_element_by_id('password'))
                    confirm_form = self.wait1s.until(lambda driver:driver.find_element_by_id('confirmPassword'))
                    captcha_form = self.wait1s.until(lambda driver:driver.find_element_by_id('recaptcha_response_field'))
                    agree_box    = self.wait1s.until(lambda driver:driver.find_element_by_id('agree'))

                    forms_found = True
                except:
                    continue

            # fill out all the forms on the sign up page
            name_form.send_keys(username)
            email_form.send_keys(username + '@gmail.com')
            pass_form.send_keys(password)
            confirm_form.send_keys(password)
            agree_box.click()
            captcha_form.click()

            # wait for user response before continuing!
            # when we see either of these two elements, we have succeeded or failed
            creating_account = True
            while creating_account:
                # the name will be in the url if you register without error.
                if username.lower() in self.driver.current_url:
                    print 'Captcha entered correctly. Would you like a cookie or a gold star?'
                    correct = True
                    creating_account = False
                elif self.driver.current_url != REGISTER_URL:
                    print 'You seem to have left the sign up page, or the page is unaccessible.'
                    break # this will force us to redirect to sign up page, which
                          # redirects us to the user profile if signed in.

        # give the okay to toss user/pass into db
        return True


    def login(self, username, password):
        try:
            LOGIN_URL = 'https://imgur.com/signin'
            self.driver.get(LOGIN_URL)
            user_field = self.wait8s.until(lambda driver:driver.find_element_by_name('username'))
            pass_field = self.wait8s.until(lambda driver:driver.find_element_by_name('password'))
            submit_button = self.wait8s.until(lambda driver:driver.find_element_by_name('submit'))
            user_field.send_keys(username)
            pass_field.send_keys(password)
            submit_button.submit()
        except:
            raise CantFindElementError(self.driver.current_url, 'login')


    def logout(self):
        if 'imgur' not in self.driver.current_url:
            self.driver.get('https://imgur.com/gallery')
        logged_out = False
        attempts = 0
        while not logged_out:
            try:
                user_button = self.wait8s.until(lambda driver:driver.find_element_by_class_name('account-user-name'))
                user_button.click()
                logout_button = self.wait8s.until(lambda driver:driver.find_element_by_link_text('logout'))
                logout_button.click()
                logged_out = True
            except:
                print 'Waiting to find logout button...'
            attempts += 1
            if attempts>10:
                raise CantFindElementError(self.driver.current_url, 'logout') # caused by https failing


    def vote(self, url_with_link, link_text, vote_up): # for vote, True is up and False is down.
        self.driver.get(url_with_link)
        try:
            link_to_img = self.wait8s.until(lambda driver:driver.find_element_by_partial_link_text(link_text))
            link_to_img.click()
        except:
            raise CantFindLinkError(url_with_link, link_text)

        try:
            if vote_up:
                button_id = 'mainUpArrow'
            else:
                button_id = 'mainDownArrow'
            vote_button = self.wait8s.until(lambda driver:driver.find_element_by_id(button_id))
            # if the button is already pushed, we don't want to remove that vote!
            if 'pushed' not in vote_button.get_attribute('class'):
                vote_button.click()
        except:
            raise CantFindElementError(self.driver.current_url, 'arrow')


    def nav_to_gallery(self):
        self.driver.get('https://imgur.com')
        try:
            next_button = self.wait8s.until(lambda driver:driver.find_element_by_class_name('post'))
            next_button.click()
        except:
            raise CantFindElementError(self.driver.current_url, 'post')


    def go_to_next(self):
        try:
            next_button = self.wait8s.until(lambda driver:driver.find_element_by_class_name('navNext'))
            next_button.click()
        except:
            raise CantFindElementError(self.driver.current_url, 'navNext')


    def auto_vote(self):
        try:
            up_counter = self.wait8s.until(lambda driver:driver.find_element_by_class_name('title positive'))
            down_counter = self.wait8s.until(lambda driver:driver.find_element_by_class_name('title negative'))
            ups = int(up_counter.text)
            downs = int(down_counter.text)
            if random.randint(0,ups+downs) < ups:
                button_id = 'mainUpArrow'
            else:
                button_id = 'mainDownArrow'
            vote_button = self.wait8s.until(lambda driver:driver.find_element_by_id(button_id))
            # if the button is already pushed, we don't want to remove that vote!
            if 'pushed' not in voteButton.get_attribute('class'):
                vote_button.click()
        except:
            raise CantFindElementError(self.driver.current_url, 'arrow')


    def comment(self, comment_text):
        try:
            comment_button = self.wait8s.until(lambda driver:driver.find_element_by_id('submit-caption-button'))
            comment_field = self.wait8s.until(lambda driver:driver.find_element_by_id('caption_textarea'))
            comment_field.click()
            comment_field.send_keys(comment_text)
            comment_button.click()
        except:
            raise CantFindElementError(self.driver.current_url, 'commentbox')


    def get_comment_text(self):
        # take caption, image, and url.
        # look for reposts and take a random good comment from there
        # if nothing found, then search for comments on page or use a viralizer comment
        comment_text = 'fag'
        return comment_text



# The purpose of this class is to provide easy access to information
# from the database as well as other randomly generated data.
class Database:
    def __init__(self):
        connection = Connection()
        db = connection['imgurbotdata']
        self.login_collection = db['logindata']
        self.proxy_collection = db['proxylist']
        # get a list of user data from database
        self.logindata = {}
        self.login_count = 0
        for account in self.login_collection.find():
            self.login_count += 1
            self.logindata[account['username']] = account
        self.usernames = self.logindata.keys()
        # get a list of proxies from database
        self.proxylist = []
        self.proxy_count = 0
        for proxy in self.proxy_collection.find():
            self.proxy_count += 1
            self.proxylist.append(proxy)
        # create indices for iterating through the data
        self.login_index = 0
        self.proxy_index = 0
        # get the nouns to make usernames
        nouns_file = open('nouns.txt')
        self.nouns = nouns_file.read().splitlines()
        nouns_file.close()
        self.NOUNS_SIZE = len(self.nouns)


    def shuffle_logins(self):
        self.login_index = 0
        for i in range(0,len(self.usernames)):
            randomIndex = random.randint(i,len(self.usernames)-1)
            tmpLogin = self.usernames[i]
            self.usernames[i] = self.usernames[randomIndex]
            self.usernames[randomIndex] = tmpLogin


    def shuffle_proxies(self):
        self.proxy_index = 0
        for i in range(0,len(self.proxylist)):
            randomIndex = random.randint(i,len(self.proxylist)-1)
            tmpProxy = self.proxylist[i]
            self.proxylist[i] = self.proxylist[randomIndex]
            self.proxylist[randomIndex] = tmpProxy


    def next_login(self):
        if self.login_index >= len(self.usernames):
            self.login_index = 0
        retval = self.logindata[self.usernames[self.login_index]]
        self.login_index += 1
        return retval


    def next_proxy(self):
        if self.proxy_index >= len(self.proxylist):
            self.proxy_index = 0
        retval = self.proxylist[self.proxy_index]
        self.proxy_index += 1
        return retval


    def fix_proxies(self, account):
        # swap proxy sets until there is at least 1 working proxy
        proxies_not_chosen = True

        # check the proxies associated with the account
        no_active_proxy = True
        proxies = account['proxies']
        for proxy in proxies:
            if self.test_proxy(proxy):
                active_proxy = proxy
                no_active_proxy = False
                break

        # if none of the proxies work, grab 3 more until one does
        attempts = 0
        while no_active_proxy:
            indices = self.make_indices(self.proxy_count, 3)
            proxies = [self.proxylist[i] for i in indices]
            for proxy in proxies:
                if self.test_proxy(proxy):
                    active_proxy = proxy
                    no_active_proxy = False
                    break
            if not no_active_proxy:
                break
            attempts += 1
            if attempts>30:
                print 'Failed to reach too many proxies. Try updating your proxies. Shutting down.'
                exit(1)

        self.login_collection.update({'_id':account['_id']},{'$set':{'proxies':proxies}},upsert=False,multi=False)
        self.logindata[account['username']]['proxies'] = proxies
        return active_proxy


    def add_login(self, username, password, proxies):
        self.login_collection.insert({'username':username,'password':password,'proxies':proxies})
        self.logindata['username'] = {'username':username,'password':password,'proxies':proxies}
        self.usernames.append(username)
        self.login_count += 1


    def add_proxy(self, proxy):
        self.proxy_collection.insert(proxy)
        self.proxylist.append(proxy)
        self.proxy_count += 1


    def clear_proxies(self):
        self.proxy_collection.remove()


    def make_name(self):
        username = ''
        # first word
        random_index = random.randint(1,self.NOUNS_SIZE) - 1
        username += self.nouns[random_index]
        # second word
        random_index = random.randint(1,self.NOUNS_SIZE) - 1
        username += self.nouns[random_index]
        # number
        random_index = random.randint(1,999)
        username += str(random_index)
        return username


    def make_pass(self):
        password = ''
        # add word
        random_index = random.randint(1,self.NOUNS_SIZE) - 1
        password += self.nouns[random_index]
        # add number
        random_index = random.randint(1,999)
        password += str(random_index)
        # if length less than 6, add another digit
        while len(password) < 6:
            password += str(random.randint(0,9))
        return password


    def make_indices(self,size,n):
        indices = []
        for i in xrange(0,n):
            randomIndex = random.randint(0,size-1)
            for index in indices:
                if randomIndex >= index:
                    randomIndex += 1
            indices.append(randomIndex)
            size -= 1
        return indices


    def test_proxy(self,proxy):
        if proxy['protocol'] != 'https':
            print ' FAILED: Wrong proxy protocol.'
            return False
        sys.stdout.write('Trying to reach '+proxy['protocol']+'://'+proxy['ip']+':'+proxy['port']+'...')
        sys.stdout.flush() # for printing at correct time
        testProxy = {proxy['protocol']:'http://'+proxy['ip']+':'+proxy['port'],
                     'http':'http://'+proxy['ip']+':'+proxy['port']}
        try:
            proxyIP = requests.get('http://icanhazip.com',proxies=testProxy,timeout=8).text
        except:
            print ' FAILED: Couldn\'t reach icanhazip.com'
            return False
        if proxy['ip'] in proxyIP:
            print ' SUCCESS'
            return True
        else:
            print ' FAILED: IP could not be confirmed.'
            return False