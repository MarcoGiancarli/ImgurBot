import sys
import pymongo
from bs4 import BeautifulSoup
import requests
import urllib

if len(sys.argv) != 4:
    print 'Invalid params! Usage: <image key> <number of votes> <up/down>'
    exit(1)


LOGIN_URL = ''
LOGUT_URL = ''
IMAGE_URL = 'https://imgur.com/' + sys.argv[1]
numVotes = int(sys.argv[2])

if sys.argv[3] == 'up':
    vote = True
elif sys.argv[3] == 'down':
    vote = False
else:
    print 'You need to specify "up" or "down" for the third param.'
    exit(1)

# go through list of proxies until valid one is confirmed
# if no valid proxies attached to account, select 3 new ones

proxies = {'https':'202.118.236.130:3128'}

response = requests.get('http://icanhazip.com',proxies=proxies)
print response.text

# login

# upvote

# logout

