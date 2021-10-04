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
import numpy as np

conn = sqlite3.connect('eg3.db')
c = conn.cursor()

def create_table():
    try:
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(date TEXT,unix REAL, tweet TEXT)")
        c.execute("CREATE INDEX date ON sentiment(date)")
        c.execute("CREATE INDEX unix ON sentiment(unix)")
        c.execute("CREATE INDEX tweet ON sentiment(tweet)")
        conn.commit()
    except Exception as e:
        print(str(e))
create_table()

#consumer key, consumer secret, access token, access secret.
class TwitterStreamer():
    def __init__(self):
        pass
    
    def stream_tweets(self):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        listener=Listener()
        auth = OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret)
        auth.set_access_token(twitter_credentials.access_token, twitter_credentials.access_token_secret)
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords: 
        stream.filter(track=['a','e','i','o','u'])

class Listener(StreamListener):

    def on_data(self, data):
        try:
            data = json.loads(data)
            tweet = data['text']
            time_ms = data['timestamp_ms']
            date=data['created_at']
            print(data)
            c.execute("INSERT INTO sentiment (date,unix, tweet) VALUES (?,?,?)",
                  (date,time_ms,tweet))
            conn.commit()

        except KeyError as e:
            print(str(e))
        return(True)

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
 
    # Authenticate using config.py and connect to Twitter Streaming API.
    
    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets()