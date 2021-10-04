# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 22:14:49 2021

@author: sjhan
"""

import streamlit as st
import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt 
import re
from streamlit_autorefresh import st_autorefresh

import stream_twitter_3
obj1=stream_twitter_3.TwitterClient()
obj2=stream_twitter_3.TweetAnalyzer()

import warnings
warnings.filterwarnings("ignore")
import time
import webbrowser
from PIL import Image

icon = Image.open('depreesion_4.jpg')
st.set_page_config(
    page_title="Twitter Analysis",
    page_icon=icon,
    layout="centered"
)

st.title("Twitter Sentimental Analysis")
from streamlit_player import st_player

st.sidebar.subheader("Choose the option ")
menu = ["Home","Details","Sentiment Analysis","Tweets of particular user","Graph"]
choice = st.sidebar.selectbox("Menu",menu) 
st.empty()
st.sidebar.subheader("Enter the tweet which u want to search for")
tweet_id = st.sidebar.text_input('tweet',value='trump')
    
if choice=="Home":
    # Embed a youtube video
    st_player("https://youtu.be/0g9Vo5RFsdU")

elif choice=="Details":
    
    image = Image.open('depreesion_1.jpg')
    st.image(image, caption='Depression')
    st.empty()
    st.write("Depression is a common mental disorder.Globally, more than 264 million people of all ages suffer from depression.Depression is a leading cause of disability worldwide and is a major contributor to the overall global burden of disease.More women are affected by depression than men.Depression can lead to suicide.There are effective psychological and pharmacological treatments for moderate and severe depression.")    
    selected=st.radio("Facts",('Depression Chart','Remedies'))
    
    if selected =='Depression Chart':
        image = Image.open('depreesion_2.jpg')
        st.image(image, caption='Chart')
    
    if selected =='Remedies':
        st.header("Online therapy can help with depression")
        st.write("Improve your quality of life with the support of BetterHelp’s licensed therapists. Speak to a therapist during a phone or video session and stay connected throughout your day with BetterHelp’s messaging platform.")
        url="https://www.betterhelp.com/get-started/?go=true&transaction_id=10235511e0872def11e6e3e73d976c&utm_source=affiliate&utm_campaign=2072&utm_medium=Desktop&utm_content=&utm_term=healthline&not_found=1&gor=start"
        st.markdown(url)   
    
    url ="https://www.healthline.com/health/depression/self-care-for-depression"
    if st.button('For more help'):
        webbrowser.open_new_tab(url)
    
    
elif choice=="Sentiment Analysis":
    
    conn = sqlite3.connect('eg1.db')
    c = conn.cursor()
    df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 1000", conn ,params=('%' + tweet_id + '%',))
    df.sort_values('unix', inplace=True)
    df['date'] = pd.to_datetime(df['unix'],unit='ms')
    df.drop('unix',axis='columns',inplace=True)
    df.set_index('date', inplace=True)
    st.table(df)
    count = st_autorefresh(interval=2000, limit=10, key="fizzbuzzcounter")
    

elif choice=="Tweets of particular user":
    
    st.subheader("Enter the username whose tweets you want to search for")
    user_id = st.text_input('user_id',value='@narendramodi')
    flag = 0
    while True:  
        if (len(user_id)<=5 or len(user_id)>15):
            flag = -1
            break
        else:
            flag = 0
            api = obj1.get_twitter_client_api()
            tweets = api.user_timeline(screen_name=user_id)
            df = obj2.tweets_to_data_frame(tweets)
            if df.empty:
                image = Image.open('depreesion_3.jpg')
                st.image(image, caption='No posts yet')
            
            else:
                st.dataframe(df.head(10))
                # Run the autorefresh about every 2000 milliseconds (2 seconds) and stop
                # after it's been refreshed 100 times.
                st.button("Refresh")
                if st.button=="Refresh":
                    # Run the autorefresh about every 2000 milliseconds (2 seconds) and stop
                    # after it's been refreshed 100 times.
                    count = st_autorefresh(interval=4000, limit=100, key="fizzbuzzcounter")
            break
      
    if flag ==-1:
        st.error("Not a Valid user_id")
    
        
elif choice=="Graph":
    
    conn = sqlite3.connect('eg1.db')
    c = conn.cursor()
    df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 1000", conn ,params=('%' + tweet_id + '%',))
    df.sort_values('unix', inplace=True)
    df['date'] = pd.to_datetime(df['unix'],unit='ms')
    plt.scatter(df['date'],df['sentiment'])
    plt.show(block=True)
            