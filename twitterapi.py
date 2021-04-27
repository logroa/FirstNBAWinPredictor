import numpy
import tweepy
from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import datetime as dt
from datetime import date

from textblob import TextBlob
from pandasql import sqldf
import pandasql as ps
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import re
import matplotlib.pyplot as plt
import os
import sqlite3
import json

consumer_key = "AUds4eS1BHAq2UcjeaBbmQi0K"
consumer_secret = "iVWKUBzAclrz1ow3XBP5ReMwAX6WUBO9NaXlCYEeiHGj5UVN7a"
access_token = "1319171958286749697-n8l6vveS4glZHOQUHxnH6ozI6ek2eI"
access_token_secret = "X9WKg1NTCmc96R9KscIpJrtQyLcHRMLF1YGuwAgT0MPy2"

path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+'stats.db')
cur = conn.cursor()

class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user
    
    def get_twitter_client_api(self):
        return self.twitter_client

    def get_tweets(self, num_tweets):
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

    def keywords_search(self, keywords, num_tweets, startDate, endDate):
        tweets = []

        data = Cursor(self.twitter_client.search, q=keywords, until=endDate, lang="en").items(num_tweets)

        while True:
          try:
              tweet = data.next()

              if tweet.retweet_count > 0:
                  if tweet not in tweets:
                      tweets.append(tweet)
              else:
                  tweets.append(tweet)

          except tweepy.TweepError: #exception for twitter rate limits
            print("Twitter's free API limit rate has been reached.  More data can be requested in fifteen minutes.  Here is what we were able to pull: ")
            break
          except Exception as e:
            break

        return tweets

class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        return auth

class TwitterStreamer():
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweet_filename, hash_tag_list):
        # handles twitter authentication and connection to twitter streaming api
        listener = TwitterListener(fetched_tweet_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        stream.filter(track=hash_tag_list)

class TwitterListener(StreamListener):
    def __init__(self, fetched_tweet_filename):
        self.fetched_tweet_filename = fetched_tweet_filename

    def on_data(self, data):
        try: 
            print(data)
            with open(self.fetched_tweet_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def on_error(self, status):
        if status == 429:
            # check for twitter rates limit to prevent banning
            return False
        print(status)

class TweetAnalyzer():
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweet_pop(self, likes, retweets):
        return 6 + 3*retweets + likes

    def actual_score(self, sentiment, likes, retweets):
        return sentiment * (6 + 3*retweets + likes)

    def tweets_to_dataframe(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])

        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])

        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

         # df['replies'] = np.array([tweet.reply_count for tweet in tweets])
         # reply_count is only part of the premium api

        df['where'] = np.array([tweet.coordinates for tweet in tweets])
        
        df['when'] = np.array([str(tweet.created_at) for tweet in tweets])

        return df

    def date_grouper(self, df):
        days = [date.split(" ")[0] for date in df['when'].values]
        df['day'] = days
        tweetsGrouped = df[['day', 'pop', 'score']].groupby('day')['pop'].agg(np.sum)
        tweetsGrouped1 = df[['day', 'pop', 'score']].groupby('day')['score'].agg(np.sum)

        df2 = pd.DataFrame({'Relevance' : tweetsGrouped, 'Popularity' : tweetsGrouped1}).reset_index()
        return df2

def db_maker(cur, conn):

    cur.execute('CREATE TABLE IF NOT EXISTS TwitterData (Date TEXT, Team_id INT, Relevance INT, Popularity INT)')
    conn.commit()

def db_add(cur, conn, team, score, pop):

    cur.execute(f'SELECT * FROM Teams WHERE Team = "{team}"')
    result = cur.fetchone()
    if result:
        ident = result[0]
    else:
        print("team not found")
        return

    now = date.today()
   # now = now.strftime("%d-%b-%Y ")
    now = str(now)
    print(type(now))

   # new_pop = int(pop)
   # print(new_pop)
  #  new_score = int(score)
 #   print(new_score)

    cur.execute(f"SELECT * FROM TwitterData WHERE Team_id = '{ident}' AND Date = '{now}'")

    result = cur.fetchone()
    if result and result[0] == now:

        twitter_dict = {}

        twitter_dict['Date'] = result[0]
        twitter_dict['Team'] = team
        twitter_dict['Relevance'] = result[2]
        twitter_dict['Popularity'] = result[3]

        return twitter_dict

    else:

        days = [date.split(" ")[0] for date in df['when'].values]
        df['day'] = days
        tweetsGrouped = df[['day', 'pop', 'score']].groupby(['day'], as_index=False)['pop'].agg(np.sum)
        tweetsGrouped1 = df[['day', 'pop', 'score']].groupby(['day'], as_index=False)['score'].agg(np.sum)
     #   tweetsGrouped = tweetsGrouped['pop']
     #   tweetsGrouped1 = tweetsGrouped['score']

        new_score = tweetsGrouped.astype(numpy.int32)
        new_pop = tweetsGrouped.astype(numpy.int32)

        print(new_score)
        print(new_pop)

        #   tweetsGrouped = tweetsGrouped.loc[0]['pop']
     #  tweetsGrouped1 = tweetsGrouped.loc[0]['score']

        print(new_pop.head())

        print(tweetsGrouped.columns.tolist())

        cur.execute("INSERT INTO TwitterData (Date, Team_id, Relevance, Popularity) VALUES (?,?,?,?)", (now, ident, new_score, new_pop))
        conn.commit()

        twitter_dict = {}

        twitter_dict['Date'] = now
        twitter_dict['Team'] = team
        twitter_dict['Relevance'] = tweetsGrouped
        twitter_dict['Popularity'] = tweetsGrouped1

        return twitter_dict

if __name__ == "__main__":
    
    team_name = input("Enter a Team Name ")

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()
  #  db_maker(cur, conn)

    tweets = twitter_client.keywords_search(team_name, 1000, dt.date.today() - dt.timedelta(days=30), dt.date.today())

    df = tweet_analyzer.tweets_to_dataframe(tweets)

    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])

    df['pop'] = tweet_analyzer.tweet_pop(df['likes'], df['retweets'])

    df['score'] = tweet_analyzer.actual_score(df['sentiment'], df['likes'], df['retweets'])

   # print(db_add(cur, conn, team_name, score, pop))
    print(team_name)

    out = tweet_analyzer.date_grouper(df)

    print(out)

    # Time Series
    time_likes = pd.Series(data=out['Relevance'])
    time_likes.plot(figsize=(16, 4), color='r')
    plt.show()
    out.plot(x='day', y=['Relevance', 'Popularity'], grid=True)