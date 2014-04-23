ImgurBot
========

ImgurBot makes it easy to quickly create imgur.com accounts, store them in a database, and vote on images with them automatically. I take no responsibility for the actions of any person who uses these scripts. Utilizes the following modules: requests, pymongo, selenium webdriver, beautiful soup. Must have Firefox installed due to webdriver dependencies, and must have mongoDB.

Usage:

    $ python updateProxies.py
    $ python creator.py numAccounts
    $ python voter.py imgTag numVotes up/down


To Do
=====

- improve proxy scraper

- implement a hijack.py script that hijacks random comments while surfing user submitted in groups of 5-10

- set up the voter script to go to the url, and change images a few times before upvoting so that it doesn't look like the user has been directly linked
