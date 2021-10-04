# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 18:01:52 2021

@author: sjhan
"""

import twitter_credentials

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
from unidecode import unidecode
from tweepy import API
from tweepy import Cursor

import sqlite3

import time
import pandas as pd
import numpy as np

from textblob import TextBlob
from deep_translator import GoogleTranslator
    
conn = sqlite3.connect('eg1.db')
c = conn.cursor()
def create_table():
    try:
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT,sentiment REAL)")
        c.execute("CREATE INDEX unix ON sentiment(unix)")
        c.execute("CREATE INDEX tweet ON sentiment(tweet)")
        c.execute("CREATE INDEX sentiment ON sentiment(sentiment)")
        conn.commit()
    
    except Exception as e:
        print(str(e))

create_table()

class TwitterClient():

    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client
    
    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets

class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret)
        auth.set_access_token(twitter_credentials.access_token, twitter_credentials.access_token_secret)
        return auth
    
class TwitterStreamer():
    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()    

    def stream_tweets(self):
        listener=Listener()
        auth = self.twitter_autenticator.authenticate_twitter_app() 
        stream = Stream(auth, listener)
        stream.filter(track=['a','e','i','o','u'])

class Listener(StreamListener):

    def on_data(self, data):
        try:
            data = json.loads(data)
            tweet = unidecode(data['text'])
            time_ms = data['timestamp_ms']
            sentiment=get_tweet_sentiment(tweet)
            print(data)
            c.execute("INSERT INTO sentiment (unix, tweet,sentiment) VALUES (?,?,?)",
                  (time_ms, tweet,sentiment))
            conn.commit()

        except KeyError as e:
            print(str(e))
        return(True)

    def on_error(self, status):
        if status == 420:
            return False
        print(status)


def get_tweet_sentiment(tweet): 
            
            translated = GoogleTranslator(source='auto', target='en').translate(tweet)
            analysis = TextBlob(translated) 
            return analysis.sentiment.polarity
               
class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """
    def tweets_to_data_frame(self, tweets):
        
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        
        df['sentiment']=df['Tweets'].apply(lambda x: get_tweet_sentiment(x))
        return df

 
if __name__ == '__main__':
 
    
    # twitter_client = TwitterClient()
    # tweet_analyzer = TweetAnalyzer()

    # api = twitter_client.get_twitter_client_api()

    # tweets = api.user_timeline(screen_name="@vijayrupanibjp", count=20)
    # df = tweet_analyzer.tweets_to_data_frame(tweets)
    
    # print(df.head(10))
    # #Authenticate using config.py and connect to Twitter Streaming API.
    
    # twitter_client = TwitterClient('@vijayrupanibjp')
    # print(twitter_client.get_user_timeline_tweets(10))
    
    #most recent tweet will be displayed
    #in this search for expanded url of display_url to know the tweet
    #and then copy the link to see the tweet
    
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets()