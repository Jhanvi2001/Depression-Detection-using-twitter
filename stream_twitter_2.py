# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 18:01:52 2021

@author: sjhan
"""

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import sqlite3
from unidecode import unidecode
import time
import twitter_credentials
from tweepy import API
from tweepy import Cursor


##1)it will setup connection 
#if the database doesnt exists then it will create new
#if it does exist, it will not be overwritten or re-created

conn = sqlite3.connect('eg2.db')
c = conn.cursor()
#cursor is like your mouse cursor
#it simply does things, like select things, delete things, add things etc.
#it does execution of things

#it helps to create table in database with certain columns and their values
def create_table():
    try:
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT)")
        c.execute("CREATE INDEX unix ON sentiment(unix)")
        c.execute("CREATE INDEX tweet ON sentiment(tweet)")
        #real=float,text
        #all caps for sql ,regular for not SQL commands

        conn.commit()
#commit is used to save the query by default it should be used as the end
    
#if the table is not created so try and except will handle the error and 
#print it instead of truncating the program
    except Exception as e:
        print(str(e))

#it will create table in database
create_table()

##2)timeline returns most recent statuses posted by user

class TwitterClient():
#it takes data that is streamed in from StreamListener ie. tweets
#it allows user to specify a username to get tweets off that user
#timeline ,if user is not specified then by default my id is taken

    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
#to authenticate
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client
    
#num_tweets tells us the number of tweets we want to extract
    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
#all the tweets get stored in this list
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
#here the timeline of the particular user is accessed and only particular no of tweets is displayed
            tweets.append(tweet)
        return tweets

#it gives followers list
    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

#it gives all the home page description ,people u follow,top tweets,following etc.
    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


#----------------------------------------------------------

#To get keys ie. consumer,authenticator etc.
#
#https://developer.twitter.com/en and sign into your acc

#
#create a new app by going into developers portal fill in the details 
#and generate consumers api and secret key as well turn on 
#OAuth and generate access token and access secret

#----------------------------------------------------------

##3)it is used authorize ourself in order to communicate with twitter
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret)
        auth.set_access_token(twitter_credentials.access_token, twitter_credentials.access_token_secret)
        return auth
    
##4)It connects us to the twitter app by writing api's needed
class TwitterStreamer():
    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()    

    def stream_tweets(self):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        listener=Listener()
        auth = self.twitter_autenticator.authenticate_twitter_app() 
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords: 
        stream.filter(track=['a','e','i','o','u'])

##5)StreamListener is a firehouse of tweets as the come based on keywords or hashtags
##It has several columns out of which tweets and timestamp is extracted
class Listener(StreamListener):

    def on_data(self, data):
        try:
            data = json.loads(data)
#Json library is used to load string from data text ie.entire chunk of data
#it is more like dictionary object
            tweet = unidecode(data['text'])
#Unicode characters as ??? or \\15BA\\15A0\\1610, to mention two extreme cases. 
#But that’s nearly useless to someone who actually wants to read what the text says.
#What Unidecode provides is a middle road: the function unidecode() takes Unicode data and tries to represent it in ASCII characters (i.e., the universally displayable characters between 0x00 and 0x7F), where the compromises taken when mapping between two character sets are chosen to be near what a human with a US keyboard would choose.
#refrence it with data text,timestamp etc.

            time_ms = data['timestamp_ms']
            print(data)
            c.execute("INSERT INTO sentiment (unix, tweet) VALUES (?, ?)",
                  (time_ms, tweet))
            conn.commit()

#for any basic exception
        except KeyError as e:
            print(str(e))
        return(True)

    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)


if __name__ == '__main__':
 
    # Authenticate using config.py and connect to Twitter Streaming API.
    twitter_client = TwitterClient('@itsdhavalhere')
    print(twitter_client.get_friend_list(10))
    #most recent tweet will be displayed
    #in this search for expanded url of display_url to know the tweet
    #and then copy the link to see the tweet
    # twitter_streamer = TwitterStreamer()
    # twitter_streamer.stream_tweets()