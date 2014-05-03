import sys


if len(sys.argv) != 5:
    print 'Invalid params! Usage: <url_with_link> <link_text> <number_of_votes> <up/down>'
    exit(1)


LOGIN_URL = 'https://imgur.com/signin'
URL_WITH_LINK = sys.argv[1]
LINK_TEXT = sys.argv[2]
NUM_VOTES = int(sys.argv[3])
voteCount = 0

if sys.argv[4] == 'up':
    vote = True
elif sys.argv[4] == 'down':
    vote = False
else:
    print 'You need to specify "up" or "down" for the third param.'
    exit(1)

db = Database()


# cycle through the shuffled account list
for account in db.logindata:

    # go through the three proxies in requests until valid one is confirmed
    # if no valid proxies attached to account, select 3 new ones from the
    # proxylist collection, update the database, and repeat
    proxy_not_chosen = True
    while proxy_not_chosen:










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
                    proxyIP = requests.get('http://icanhazip.com',proxies=testProxy,timeout = 5).text
                    if proxy['ip'] in proxyIP:
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
            indices = genIndices(len(proxylist))
            for index in indices:
                proxies.append(proxylist[index])

    # update database with current proxies
    logindataCollection.update({'_id':account['_id']},{'$set':{'proxies':proxies}},upsert=False,multi=False)


    ########## BEGIN SELENIUM ##########

    workingProxies = Proxy({'httpProxy' : workingProxy['ip'] + ':' + workingProxy['port']})
    firefox = webdriver.Firefox(proxy=workingProxies)
    wait = WebDriverWait(firefox, 8)

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
            exit(1)

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
    print 'Number of votes: '+voteCount

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
