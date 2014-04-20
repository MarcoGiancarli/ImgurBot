ImgurBot
========

ImgurBot makes it easy to quickly create imgur.com accounts, store them in a database, and upvote with them automatically. Disclaimer: DO NOT USE THIS. I take no responsibility for the actions of any person who uses this software. Utilizes the following modules: requests, pymongo, selenium webdriver, beautiful soup. Must have Firefox installed due to webdriver dependencies, and must have mongoDB.

Usage:

$ python updateProxies.py

$ python creator.py <'numAccounts'>

$ python voter.py <'imgTag'> <'numVotes'> <'up'/'down'>


To Do
=====

-finish proxy scraper

-finsh implementing mongo

-set up loop to fix broken proxies

-set up main loop for dbs in upvoter

-finish main loop in creator
