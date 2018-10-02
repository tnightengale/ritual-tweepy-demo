import urllib.request as url
from bs4 import BeautifulSoup
import re
import tweepy
from tweepy import OAuthHandler
import json
from random import randrange
import time
import datetime

# error handling for streaming
# no longer necessary because of
# checking implementation
from requests.exceptions import Timeout, ConnectionError
from requests.packages.urllib3.exceptions import ReadTimeoutError
from OpenSSL.SSL import WantReadError


def main():
    '''
    Calls the main initializations
    to build the client list and 
    run the tweepy stream.
    '''
    client_init()
    
    #print('Initializing stream...')
    #stream_init()
    
    print('Initializing checking routine...')
    static_search(api=api_init(),username='@lunchatron9000')
    


def stream_init():
    '''
    Initializes the tweepy stream by calling api_init()
    and using the return api object to create a stream.
    This process is called here so that it can be recalled
    in the event that the stream times out. In this way the
    stream can run indefinitely. 
    '''
    api = api_init()
    
    myStreamListener = MyStreamListener(api)
    myStream = tweepy.Stream(auth=api.auth,listener=myStreamListener)
    monitor = '@' + api.me().screen_name
    
    myStream.filter(track=[monitor], async=True)


def api_init():
    '''
    Initializes the api object used with
    tweepy API, using keys stored in a 
    JSON file.
    '''
    # open json with keys and assign keys
    with open('/Users/tnightengale/Desktop/Projects/Ritual_Tweepy/'+"authentication.json", "r") as read_file:
        keys = json.load(read_file)
        
    consumer_key = keys['lunchatron9000']['(API key)']
    consumer_secret = keys['lunchatron9000']['(API secret key)']
    access_token = keys['lunchatron9000']['(Access token)']
    access_secret = keys['lunchatron9000']['(Access token secret)']
     
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    return api
    
    
def ritual_establishments(site='https://order.ritual.co/city/toronto', n_pages=2):
    '''
    Takes in the url of the ritual website and 
    the number of pages to scrape, and returns
    a list of establishments names and a ordered
    matching list of urls offered on the Ritual site.
    '''
    
    pg_extensions = ['?page=' + str(i) for i in range(1,n_pages+1)]
    
    names = []
    ids = []
    
    for extension in pg_extensions:
        
        with url.urlopen(site + extension) as current_page:
            #current_page = url.urlopen(site + extension)
            soup = BeautifulSoup(current_page, 'html.parser')
            
            taglist = soup.find_all('h2','card-title')
            idlist = soup.find_all('div','card-marker')
            
            # create restaurant id extension to recreate url later
            exten0 = re.search('.+?(?=city)',site).group(0) + 'menu/'
            
            
            exten1 = [exten0+_.string.lower().replace("'",'').replace(' ','-').replace('(','').replace('/','-').replace(')','-').replace('--','-') for _ in taglist]
            
            
            exten2 = [str(item) for item in idlist]
            exten2 = [re.search('card_marker_....',_).group(0) for _ in exten2]
            exten2 = ['toronto/' + item.split('_')[2] for item in exten2]
            
            exten = [i+j for i,j in zip(exten1,exten2)]
            
            
            # clean names
            establishments = [_.string for _ in taglist]
            establishments = [re.search('[^(]*',_).group(0) for _ in establishments]
            establishments = [_.rstrip(' ') for _ in establishments]
            
            names.append(establishments)
            ids.append(exten)
    
    names = [i for j in names for i in j]
    ids = [i for j in ids for i in j]
    return names, ids


def client_init():
    global extensions
    global clients
    clients, extensions = ritual_establishments()


#override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):
    
    def __init__(self, api, dump_json=False, numtweets=0):
        self.api = api
        self.dump_json = dump_json
        self.count = 1
        self.limit = int(numtweets)
    
    def on_status(self, status):
        # process tweet
        while True:
            try:
                text = status.text
                sender = '@' + status.user.screen_name
                print('Incoming tweet from {}: {}'.format(sender,text))
                
                if 'lunch' in text:
                    r = randrange(len(clients))
                    reply = "{} You should try {}! Order ahead with Ritual so everything is ready when you arrive! Here's the link: {}".format(sender,clients[r],extensions[r])
                    print('Replied with: {}'.format(reply))
                    self.api.update_status(reply)
            except (Timeout,ConnectionError,ReadTimeoutError,WantReadError) as e:
                print('Time out error caught: {}'.format(e))
                time.sleep(30)
                continue
            

    def on_timeout(self):
        stream_init()
	
    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False

def static_search(api,username):
    '''
    Takes in an api and the corresponding
    username to monitor the account in an
    infinite loop and reply to requests. 
    In this case the reply is immutable 
    within this function, and specific 
    to the lunchatron9000 bot.
    '''
    
    while True:
        
        latest_mention = api.search(username,count=1)[0]
        
        # wait to check for new mentions
        seconds = 60*45 
        time.sleep(seconds)
        
        new_mention = api.search(username,count=1)[0]
        
        if latest_mention.id == new_mention.id:
            print('No new mentions at time: {}'.format(datetime.datetime.now()))
            print('Will recheck in {} minutes'.format(int(seconds/60)))
            pass
        
        else:
            status = new_mention
            text = status.text
            sender = '@' + status.user.screen_name
            print('Incoming tweet from {}: {}'.format(sender,text))
            checks = ['eat','have', ' lunch ']
            
            if any(word in text for word in checks):
                
                r = randrange(len(clients))
                reply = "{} You should try {}! Order ahead with Ritual so everything is ready when you arrive! Here's the link: {}".format(sender,clients[r],extensions[r])
                print('Replied with: {}'.format(reply))
                api.update_status(reply)
            
            else:
                reply = "I can't answer that. Beep Boop."
                print('Replied with: {}'.format(reply))
                api.update_status(reply)
        
        
            
    
    
    
    


if __name__== '__main__':
    main()
