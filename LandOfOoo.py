'''
Created on Nov 23, 2013

@author: felix
@author: leftbigtoe
'''

# modules we're using (you'll need to download lxml)
import lxml.html, urllib2, urlparse, os, re, sys, time
from mechanize import Browser
from Daemon import Daemon


"""
core of the adventureStream
fetches & saves a list of links with all episodes
can play episodes
"""
class Enchiridion:

    def __init__(self, base_url):
        # initialize with infinity, so first update will not be sth new
        self.base_url = base_url
        # create class variables
        self.nEpisodes = float('inf')
        self.links = []
        self.ns = {}
        # initial update
        self.updateLinks(printFlag = True)


    def __countEpisodes__(self):
        self.nEpisodes = len(self.links)


    def correct(self, i):
        if i > len(self.links):
            return False
        try:
            urllib2.urlopen(self.links[i]) 
        except:
            return False
        return True
    

    def updateLinks(self, printFlag = True):  
        # fetch the page
        res = urllib2.urlopen(self.base_url)

        # parse the response into an xml tree
        tree = lxml.html.fromstring(res.read())

        # construct a namespace dictionary to pass to the xpath() call
        # this lets us use regular expressions in the xpath
        self.ns = {'re': 'http://exslt.org/regular-expressions'}

        # iterate over all <a> tags whose href ends in ".pdf" (case-insensitive)
        self.links = [urlparse.urljoin(self.base_url, node.attrib['href']) 
                 for node in tree.xpath('//a[re:test(@href, "adventure-time-season", "i")]', 
                    namespaces=self.ns)]
        # update number of episodes in the link library
        self.__countEpisodes__()


    def listEpisodes(self):
            # print the href, joining it to the self.base_url
          #  print (i, urlparse.urljoin(self.base_url, node.attrib['href']))
        for i in range(len(self.links)):
            print '[%d] %s' %(i, self.links[i])

        
    def playEpisode(self,episode):
        # select episode     
        selected_url = self.links[episode]

        print 'selected episode: ', selected_url

        # fetch the page
        res = urllib2.urlopen(selected_url)

        # parse the response into an xml tree
        tree = lxml.html.fromstring(res.read())

        links = [urlparse.urljoin(selected_url, node.attrib['src']) 
                 for node in tree.xpath(
                    '//iframe[re:test(@src, "http://www.animeuploads.com/","i")]', 
                    namespaces=self.ns)]
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

"""
daemon thread running in the background that checks every checkIntervalMin if there's a new
episode and will then ask you to watch it
"""
class AdventureDaemon(Daemon):
    

    def __init__(self,enchiridion, checkIntervalMin = 0.5):
        super(AdventureDaemon, self).__init__('/tmp/adventureDaemon.pid')

        self.enchiridion = enchiridion
        self.checkInterval = checkIntervalMin

        self.tmpFileName = ".tmpFile.ats"
        # if daemon is executed first time, create an initial tmpFile
        if not os.path.isfile(self.tmpFileName):
            self.writeTmpFile()


    def writeTmpFile(self):
        tmpFile = open(self.tmpFileName, "wr")
        tmpFile.write(str(enchiridion.nEpisodes))
        tmpFile.close()


    def readTmpFile(self):
        try:
            tmpFile = open(self.tmpFileName, "r")
        except:
            # TODO make this write to an error log file
            sys.stderr.write("couldn't find tmp file")
        n = int(tmpFile.read())
        tmpFile.close()
        return n
        


    """
    overwritten method of the motherclass Daemon
    """
    def run(self):
        while True:
            oldNumber = self.readTmpFile()
            enchiridion.updateLinks()
            self.writeTmpFile()

            # wanna watch?
            if oldNumber < self.readTmpFile():
                print "WHAT TIME IS IT? ADVENTURE TIME!!!!"
                yn = input("new episode bro! wanna watch? 1 = yes: ")
                if yn == 1:
                    enchiridion.playEpisode(1)
                else:
                    print "ahhhh, you're lame man! I'm gonna watch it with BMO..."
            else:
                "naaah man, nothin new..."

            # check for new episodes every 30min
            time.sleep(60 * self.checkInterval)






# boiler plate
if __name__ == "__main__":

    # the url of the page you want to scrape
    base_url = 'http://www.watchcartoononline.com/anime/adventure-time'

    # starting up the class saving the links & playing the episodes
    enchiridion = Enchiridion(base_url)

    # play latest episode
    if sys.argv[-1] == '-l':
        enchiridion.playEpisode(1)

    # start daemon watcher
    elif sys.argv[-1] == '-w':
        print "Starting AdventureDaemon..."
        adventureDaemon = AdventureDaemon(enchiridion)
        adventureDaemon.run()
        sys.exit(0)

    # stop daemon watcher
    elif sys.argv[-1] == '-s':
        print "shutting down the AdventureDaemon..."
        adventureDaemon = AdventureDaemon(enchiridion)
        adventureDaemon.stop()
        sys.exit(0)
        
    else:
        enchiridion.listEpisodes()
        while True:
            episode = input('hey bro, type episode number you wanna watch'+ 
                            'or "exit()" to get out of here: ')
            if episode == 'exit':
                break
            elif episode == 'list':
                enchiridion.listEpisodes()
            elif enchiridion.correct(episode):
                enchiridion.playEpisode(episode)
            else:
                "sorry bro, not a valid episode"

