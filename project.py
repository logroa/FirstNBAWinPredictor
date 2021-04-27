import json
import unittest
import os
import requests
import team_stats as ts
import nbaapi as nba
import sqlite3
import twitterapi as ta
import advancednba as an
import regressionmodeling as rm

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

#
# Your name: Grant Marshall
# Who you worked with:
#
#commit

path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+'stats.db')
cur = conn.cursor()

team = input("Enter a team name with capitalized first letters and the city (ex. Washington Wizards): ")
print("")

abrevs = ts.team_abrevs()
cur.execute('CREATE TABLE IF NOT EXISTS Teams (id INTEGER PRIMARY KEY, Team TEXT, Abbreviation TEXT)')
cur.execute("SELECT * FROM Teams")
result = cur.fetchone()
if not result:
    for key in abrevs:
        cur.execute('INSERT INTO Teams (Team, Abbreviation) VALUES (?, ?)', (key, abrevs[key]))
    conn.commit()

opponent = ""
siteList = nba.odds_finder(team)
if siteList != None:
    oddsList = []
    for i in siteList:
        oddsList.append((i[0], i[1], nba.winPercCalc(i[1]), i[2], i[3]))
    nba.outputter(team, oddsList)
    opponent = oddsList[0][4]
    if len(oddsList) < 17:
        print("Game has likely already started, so the lines above are LIVE LINES")

    else:
        nba.dbMaker(cur, conn)
        nba.dbAddition(team, oddsList, cur, conn)

print("")
stats = ts.stats(team)
for keys in stats:
    print(keys + ": " + str(stats[keys]))
print("")
ostats = ts.stats(opponent)
for keys in ostats:
    print(keys + ": " + str(ostats[keys]))

print("")
ts.compare_teams(team, opponent)
print("")

twitter_client = ta.TwitterClient()
tweet_analyzer = ta.TweetAnalyzer()
api = twitter_client.get_twitter_client_api()

tweets = twitter_client.keywords_search(team, 1000, dt.date.today()-dt.timedelta(days=30), dt.date.today())

df = tweet_analyzer.tweets_to_dataframe(tweets)

df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])

df['pop'] = tweet_analyzer.tweet_pop(df['likes'], df['retweets'])

df['score'] = tweet_analyzer.actual_score(df['sentiment'], df['likes'], df['retweets'])

out = tweet_analyzer.date_grouper(df)

print(out)

# Time Series
time_likes = pd.Series(data=out['Relevance'])
time_likes.plot(figsize=(16, 4), color='r')
out.plot(x='day', y=['Relevance', 'Popularity'], grid=True)

rm.modelMaker(team)