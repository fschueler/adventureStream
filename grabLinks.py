'''
Created on Nov 23, 2013

@author: felix
'''
# modules we're using (you'll need to download lxml)
import lxml.html, urllib2, urlparse, os, re, sys
from mechanize import Browser
# the url of the page you want to scrape
base_url = 'http://www.watchcartoononline.com/anime/adventure-time'

def correct(i):
    if i > len(links):
        return False
    try:
        urllib2.urlopen(links[i]) 
    except:
        return False
    return True
    
# fetch the page
res = urllib2.urlopen(base_url)

# parse the response into an xml tree
tree = lxml.html.fromstring(res.read())

# construct a namespace dictionary to pass to the xpath() call
# this lets us use regular expressions in the xpath
ns = {'re': 'http://exslt.org/regular-expressions'}

# iterate over all <a> tags whose href ends in ".pdf" (case-insensitive)
links = [urlparse.urljoin(base_url, node.attrib['href']) for node in tree.xpath('//a[re:test(@href, "adventure-time-season", "i")]', namespaces=ns)]

    # print the href, joining it to the base_url
  #  print (i, urlparse.urljoin(base_url, node.attrib['href']))
for i in range(len(links)):
    print '[%d] %s' %(i, links[i])

if sys.argv[-1] == '-l':
    episode = 1
else:
    while True:
        episode = input('please select episode: ')
        if correct(episode):
            break
    

    
    
selected_url = links[episode]

print 'selected episode: ', selected_url

# fetch the page
res = urllib2.urlopen(selected_url)

# parse the response into an xml tree
tree = lxml.html.fromstring(res.read())

links = [urlparse.urljoin(selected_url, node.attrib['src']) for node in tree.xpath('//iframe[re:test(@src, "http://www.animeuploads.com/", "i")]', namespaces=ns)]
for i in range(len(links)):
    print '%d %s' %(i, links[i])

selected_url = links[0]
print 'selected animeuploads-link: ', selected_url


br = Browser()
page = br.open(selected_url)
br.select_form(nr = 0)
pag2 = br.submit()
html = pag2.read()

regex = re.compile("file=(http[^/]+%.*flv)",re.IGNORECASE|re.MULTILINE)
streamlinks = regex.findall(html)
print 'selected streamlink before cleaning: %s' %streamlinks[0]
videolink = re.sub("(%2F)", '/', streamlinks[0])
videolink = re.sub("(%3A)", ':', videolink)


print 'streaming video from %s' %videolink
#videolink is in html --> filter for file=http%3A%2F%2Fl2.watchanimesub.net%2F180bdfd310df8a4129ec22836bfd9822%2F52901ac6%2Fputlocker%2F038C9B165CD09982.flv

#videolink = 'http://l2.watchanimesub.net/c62a74bfe7204b33b02a87e72c63cbea/528fdd92/putlocker/038C9B165CD09982.flv'
    
os.system('vlc -vvv %s' %videolink)


