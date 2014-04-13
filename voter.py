import sys
import pymongo
from bs4 import BeautifulSoup as soup
import requests

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

proxies = {'http':'http://221.176.14.72:80'}
response = requests.get('http://icanhazip.com',proxies=proxies)
print 'Using IP',response.text

# login
# wait a bit
# upvote
# wait some more
# logout
# rinse & repeat
