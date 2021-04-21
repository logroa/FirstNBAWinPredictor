import json
import unittest
import os
import requests
import team_stats as ts
import nbaapi as np
import sqlite3
import advancednba as an

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
stats = ts.stats(team)
for keys in stats:
    print(keys + ": " + str(stats[keys]))
print("")

#advanced = an.statFinder()
#print(advanced)
#print("")

siteList = np.odds_finder(team)
if siteList != None:
    oddsList = []
    for i in siteList:
        oddsList.append((i[0], i[1], np.winPercCalc(i[1]), i[2], i[3]))
    np.outputter(team, oddsList)
    if len(oddsList) < 17:
        print("Game has likely already started, so the lines above are LIVE LINES")

    else:
        dbMaker(cur, conn)
        dbAddition(team, oddsList, cur, conn)

print("")