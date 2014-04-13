import requests
import sys

if len(sys.argv) != 4:
    print 'Invalid params! Usage: <image key> <number of votes> <up/down>'
    exit(1)

imageUrl = 'https://imgur.com/' + sys.argv[1]
numVotes = int(sys.argv[2])

if sys.argv[3] == 'up':
    vote = True
elif sys.argv[3] == 'down':
    vote = False
else:
    print 'You need to specify "up" or "down" for the third param.'
    exit(1)

proxyDict = {'https':'184.182.240.131:19315'}
response = requests.get('http://icanhazip.com', proxies=proxyDict)
print response.text
# login

# upvote

# logout

