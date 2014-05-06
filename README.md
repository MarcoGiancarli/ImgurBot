ImgurBot
========

ImgurBot allows users to quickly create many imgur.com accounts, store them in a database, and vote on images with them automatically.

This project currently has four scripts: 

1. updateProxies.py scrapes the web for proxies, and stores them in the database.
2. creator.py uses these proxies to create new users with names and passwords randomly generated from the nouns.txt file. it then assigns 3 random proxies to this user, and confirms that at least one of them is up. If not, it removes these proxies and assigns 3 more. Then, a webdriver instance will simulate registering the account. Currently, everything is automated except for the ReCaptcha, which must be completed manually. Once an account has been created successfully, it is stored into the database, along with its associated proxies.
3. browse.py isn't totally necessary, but the purpose of this script is to simulate a user browsing imgur. It will go through posts, commenting and voting on a few, and eventually it will log off and log in as a different user.
4. voter.py pulls the accounts from the database, shuffles them, and begins to cycle through them. A webdriver instance will be created with the first working proxy associated with the account. If there isn't a working proxy, the proxies are replaced with new ones from the database. The webdriver will then log in to the account, vote on a particular post, logout, and repeat.

Utilizes the following modules: 

- Requests
- PyMongo
- Selenium WebDriver
- Beautiful Soup

Usage:

    $ python updateProxies.py
    $ python creator.py num_accounts

    $ python browse.py
    $ python voter.py url_with_link link_text num_votes up/down


To Do
=====

- Improve name/password creator. The names aren't realistic enough.
- Improve proxy scraper to gather more/better proxies.
- Implement a browse.py script that simulates browsing user submitted in groups of 5-10 users. Use Selenium Grid for this.
- Edit the voter.py script to go to the url, and change images a few times before upvoting so that it doesn't look like the user has been directly linked to the post. Maybe link from reddit instead.
