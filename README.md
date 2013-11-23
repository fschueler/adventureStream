adventureStream
===============

A python script to stream adventure time episodes to vlc media player under ubuntu (not tested for any other system)

The script emulates the behaviour of browsing watchcartoononline.com and look for adventure time episodes. Everyone of us knows this from daily life so this little script should help.
Furthermore it frees you from embedded flash players! (yey!)
Until now it works for the most recent episodes, other episodes throw a 404 error - you're welcome to fix this!


run the script
--------------
you will need the python package mechanize

    sudo apt-get install python-mechanize
    
then run the script with

    python grabLinks.py [options]


options include (until now):

    -l:  streams the latest episode
    -w:  starts AdventureDaemon that watches for new episodes
    -s:  shuts down AdventureDaemon
