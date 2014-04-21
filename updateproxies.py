import pymongo
import requests
from bs4 import BeautifulSoup as Soup

connection = pymongo.Connection()
db = connection['imgurbotdata']
proxylist = db['proxylist']

# clear old proxylist
proxylist.remove()

#HIDEMYASS_URL = 'https://hidemyass.com/proxy-list/search-226830'
#LETUSHIDE_URL = 'http://letushide.com/filter/http,ntp,us/list_of_free_HTTP_None_Transparent_US_United_States_proxy_servers'
#PROXYNOVA_URL = 'http://www.proxynova.com/proxy-server-list/country-us/'
#INCLOAK_URL = 'http://incloak.com/proxy-list/?country=US&type=h&anon=234'

#hidemyassHTML = requests.get(HIDEMYASS_URL).text
#letushideHTML = requests.get(LETUSHIDE_URL).text
#proxynovaHTML = requests.get(PROXYNOVA_URL).text
#incloakHTML = requests.get(INCLOAK_URL).text

#hidemyass = Soup(hidemyassHTML)
#letushide = Soup(letushideHTML)
#proxynova = Soup(proxynovaHTML)
#incloak = Soup(incloakHTML)

numFound = 0


# Hide My Ass
#rows = hidemyass.find_all(lambda tag:tag.name=='tr' and tag.has_attr('class'))
#for row in rows:
#    fields = row.find_all('td')
#    # get ip, port, and protocol for proxy
#    ip = fields[1].get_text()
#    port = fields[2].get_text()
#    protocol = fields[6].get_text().lower()
#    # store proxy in database
#    proxylist.insert({'ip':ip,'port':port,'protocol':protocol})
#    numFound += 1


# Let Us Hide
pages = [
        'http://letushide.com/filter/http,ntp,all/list_of_free_HTTP_None_Transparent_proxy_servers',
        'http://letushide.com/filter/http,ntp,all/2/list_of_free_HTTP_None_Transparent_proxy_servers',
        'http://letushide.com/filter/http,ntp,all/3/list_of_free_HTTP_None_Transparent_proxy_servers',
        'http://letushide.com/filter/http,ntp,all/4/list_of_free_HTTP_None_Transparent_proxy_servers',
        'http://letushide.com/filter/http,ntp,all/5/list_of_free_HTTP_None_Transparent_proxy_servers',
        'http://letushide.com/filter/http,ntp,all/6/list_of_free_HTTP_None_Transparent_proxy_servers']
for page in pages:
    letushide = Soup(requests.get(page).text)
    rows = letushide.find_all('tr',{'id':'data'})
    for row in rows:
        fields = row.find_all('td')
        # get ip, port, and protocol for proxy
        ip = fields[1].get_text()
        port = fields[2].get_text()
        protocol = fields[3].get_text().lower()
        # store proxy in database
        proxylist.insert({'ip':ip,'port':port,'protocol':protocol})
        numFound += 1


# Proxy Nova
#rows = proxynova.find_all('tr',{'id':'data'})
#for row in rows:
#    fields = row.find_all('td')
#    # we need to ignore an ad row in the middle
#    if len(fields) > 1:
#        # get ip and port for proxy, assume http
#        ip = fields[0].get_text()
#        port = fields[1].get_text()
#        # store proxy in database if it's not transparent
#        if fields[5] != 'Transparent':
#            proxylist.insert({'ip':ip,'port':port,'protocol':'http'})
#            numFound += 1


# In Cloak
#rows = proxynova.find_all('tr')
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
for proxy in proxylist.find():
    ip = proxy['ip']
    port = proxy['port']
    protocol = proxy['protocol']
    print ip,' '*(17-len(ip)),port,' '*(6-len(port)),protocol

