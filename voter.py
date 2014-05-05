from imgurbot import *
import sys


if len(sys.argv) != 5:
    print 'Invalid params! Usage: <url_with_link> <link_text> <number_of_votes> <up/down>'
    exit(1)


URL_WITH_LINK = sys.argv[1]
LINK_TEXT = sys.argv[2]
NUM_VOTES = int(sys.argv[3])
vote_count = 0
db = Database()
db.shuffle_logins()

if sys.argv[4] == 'up':
    vote_up = True
elif sys.argv[4] == 'down':
    vote_up = False
else:
    print 'You need to specify "up" or "down" for the third param.'
    exit(1)


# cycle through the shuffled account list
accounts = [db.logindata[username] for username in db.usernames]
for account in accounts:

    not_voted = True
    while not_voted:
        active_proxy = db.fix_proxies(account)

        try:
            print 'Attempting to vote on account',account['username'],'('+account['password']+')...'
            bot = Imgurbot(active_proxy)
            bot.login(account['username'], account['password'])
            bot.vote(URL_WITH_LINK, LINK_TEXT, vote_up)
            print 'Successfully voted on account',account['username']
            vote_count += 1
            not_voted = False
            bot.logout()
            bot.driver.quit()
        except BadProxyError:
            print 'Selenium can\'t reach the proxy. Making another account...'
            print 'BAD PROXY ERROR: The apparent IP when accessing the web is incorrect.'
        except CantReachProxyError:
            print 'Selenium can\'t reach the proxy. ...'
            print 'CANT REACH PROXY ERROR: Proxy seems to be offline.'
        except CantFindLinkError:
            bot.driver.quit()
            print 'Selenium has encountered a problem: the link provided does not contain the link text.'
            print 'Verify that your parameters are correct.'
        except CantFindElementError:
            bot.driver.quit()
            print 'Selenium has encountered a problem: couldn\'t find logout button.'
            print 'Account voted successfully, but failed to exit normally.'
    if vote_count >= NUM_VOTES:
        break


########## RESULTS ##########

if vote == True:
    print 'Successful upvotes:', voteCount
if vote == False:
    print 'Successful downvotes:', voteCount
