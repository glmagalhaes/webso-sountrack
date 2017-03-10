import urllib
import urllib2
from bs4 import BeautifulSoup

textToSearch = 'scarlett johansson and joaquin phoenix the moon song'
query = urllib.quote(textToSearch)
url = "https://www.youtube.com/results?search_query=" + query
response = urllib2.urlopen(url)
html = response.read()
soup = BeautifulSoup(html, "html5lib")
for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
    if not vid['href'].startswith("https://googleads.g.doubleclick.net/"):
        print 'https://www.youtube.com' + vid['href']
