from selenium import webdriver
from imgurbot import *
from bs4 import BeautifulSoup as Soup
import requests

# clear old proxylist
db = Database()
db.clear_proxies()

driver = webdriver.PhantomJS()
numFound = 0


# Hide My Ass
# We can't use requests+soup for this because HMA obfuscates their proxies
page = 'https://www.hidemyass.com/proxy-list'
try:
    driver.get(page)
    inputs = driver.find_elements_by_tag_name('input')
    inputs[3].click()  # unselect http proxies
    inputs[5].click()  # unselect socks proxies
    inputs[6].click()  # unselect transparent proxies
    inputs[7].click()  # unselect low anonymity proxies
    inputs[12].click() # unselect slow speed proxies
    inputs[15].click() # unselect slow connection proxies
    inputs[19].click() # update results
    rows = driver.find_elements_by_tag_name('tr')
    row = 1 # ignore title row
    while row<len(rows):
        fields = rows[row].find_elements_by_tag_name('td')
        # get ip, port, and protocol for proxy
        ip = fields[1].text
        port = fields[2].text
        protocol = fields[6].text.lower()
        # store proxy in database
        db.add_proxy({'ip':ip,'port':port,'protocol':protocol})
        numFound += 1
        row += 1
except:
    print 'Could not reach the HideMyAss site.'


# Let Us Hide
pages = ['http://letushide.com/filter/https,ntp,all/list_of_free_HTTPS_None_Transparent_proxy_servers',
         'http://letushide.com/filter/https,ntp,all/2/list_of_free_HTTPS_None_Transparent_proxy_servers',
         'http://letushide.com/filter/https,ntp,all/3/list_of_free_HTTPS_None_Transparent_proxy_servers']

for page in pages:
    try:
        letushide = Soup(requests.get(page,timeout=3).text)
    except:
        print 'Cant reach a page in LetUsHide:\n'+page
        continue
    rows = letushide.find_all('tr',{'id':'data'})
    for row in rows:
        fields = row.find_all('td')
        # get ip, port, and protocol for proxy
        ip = fields[1].get_text()
        port = fields[2].get_text()
        protocol = fields[3].get_text().lower()
        # store proxy in database
        db.add_proxy({'ip':ip,'port':port,'protocol':protocol})
        numFound += 1


# Spys.ru
page = 'http://spys.ru/en/https-ssl-proxy'
#try:
driver.get(page)
print 'got to spys.ru site'
driver.find_element_by_id('xpp').click()
driver.find_element_by_xpath('//select/option[@value=3]').click() # 200 proxies per page
driver.find_element_by_id('xf1').click()
driver.find_element_by_xpath('//select/option[@value=1]').click() # only anonymous proxies
print 'clicked buttons on spys.ru'
rows = driver.find_elements_by_tag_name('tr')
row = 8 # ignore title row
while row<len(rows):
    print 'checking row',row
    fields = rows[row].find_elements_by_tag_name('td')
    # get ip, port, and protocol for proxy
    print 'fuck you'
    for field in fields:
        print field.text
        if field.get_attribute('class') in 'spy14':
            ip_port = field.text.split(':')
            break
    print 'got ip/port:', ip_port
    ip = ip_port[0]
    port = ip_port[1]
    protocol = fields[1].text.lower()
    # store proxy in database
    db.add_proxy({'ip':ip,'port':port,'protocol':protocol})
    numFound += 1
    row += 1
#except:
#    print 'Could not reach the spys.ru site.'


# In Cloak
#rows = incloak.find_all('tr')
#for row in rows:
#    fields = row.find_all('td')
#    if len(fields) > 1:
#        # get ip and port for proxy, assume http
#        ip = fields[0].get_text()
#        port = fields[1].get_text()
#        # store proxy in database, ignore table titles
#        if port.isdigit():
#            proxylist.insert({'ip':ip,'port':port,'protocol':'http'})
#            numFound += 1


########## RESULTS ##########
print ' --',numFound,'Proxies Found -- '
print 'IP                 Port    Protocol'
for proxy in db.proxylist:
    ip = proxy['ip']
    port = proxy['port']
    protocol = proxy['protocol']
    print ip,' '*(17-len(ip)),port,' '*(6-len(port)),protocol
print 'Proxy count in database:',numFound
