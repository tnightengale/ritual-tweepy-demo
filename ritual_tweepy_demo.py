
# coding: utf-8

# In[1]:


import urllib.request as url
from bs4 import BeautifulSoup
import re
import tweepy
from tweepy import OAuthHandler
import json
from random import randrange


# In[13]:


def ritual_establishments(site, n_pages):
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
        
        current_page = url.urlopen(site + extension)
        soup = BeautifulSoup(current_page, 'html.parser')
        
        taglist = soup.find_all('h2','card-title')
        idlist = soup.find_all('div','card-marker')
        
        # create restaurant id extension to recreate url later
        exten0 = re.search('.+?(?=city)',ritual_site).group(0) + 'menu/'
        
        
        
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


# In[14]:


ritual_site = 'https://order.ritual.co/city/toronto'


# In[15]:


clients, extensions = ritual_establishments(ritual_site,2)


# In[32]:


global extensions
global clients
c_key = ''
cs_key = ''
a_token = ''
as_token = ''


# In[2]:


consumer_key = c_key
consumer_secret = cs_key
access_token = a_token
access_secret = as_token
 
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
 
api = tweepy.API(auth)


# In[3]:


tweepy.Cursor(api.followers).items().next


# In[4]:


def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)

for follower in limit_handled(tweepy.Cursor(api.followers).items()):
    print(follower.screen_name)


# In[36]:


#override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):
    
    def __init__(self, api, dump_json=False, numtweets=0):
        self.api = api
        self.dump_json = dump_json
        self.count = 1
        self.limit = int(numtweets)
    
    def on_status(self, status):
        # process tweet
        text = status.text
        sender = '@' + status.user.screen_name
        
        if 'lunch' in text:
            r = randrange(len(clients))
            reply = reply = "{} You should try {}! Order ahead with Ritual so everything is ready when you arrive! Here's the link {}".format(sender,clients[r],extensions[r])
            api.update_status(reply)        
    
    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False


# In[37]:


myStreamListener = MyStreamListener(api)


# In[38]:


myStream = tweepy.Stream(auth=api.auth,listener=myStreamListener)


# In[39]:


monitor = '@' + api.me().screen_name


# In[ ]:


myStream.filter(track=[monitor])

