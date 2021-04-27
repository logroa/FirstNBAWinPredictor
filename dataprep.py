from bs4 import BeautifulSoup
import requests
import os
import json
import sqlite3
from datetime import date

def askDate():
    while True:
        x = input("Please enter a date in YYYYmmdd format (Ex. 20210426): ")
        tods = str(date.today())
        num = tods[0:4] + tods[5:7] + tods[8:10]
        if int(x) >= int(num):
            print("Please enter a data that has completed games played")
        elif int(x) > 20210415:
            break
        else:
            print("Please enter a more recent data.")
    return x

def abrvConverter(abr):
    teams = {
        "SA": "SAS",
        "GS": "GSW",
        "NY": "NYK",
        "WSH": "WAS",
    }
    if abr in teams:
        return teams[abr]
    else:
        return abr

def winFinder():
    dater = askDate()
    url = "https://www.espn.com/nba/schedule/_/date/" + dater
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    outer = soup.find('div', id="sched-container")
    inner = outer.find('div', class_="responsive-table-wrap").find('tbody')
    games = inner.find_all('tr')

    scores = []

    for i in games:
        dp = i.find_all('td')
        wl = dp[2].text.split()
        scores.append(((dater[0:4] + "-" + dater[4:6] + "-" + dater[6:]), abrvConverter(wl[0]), abrvConverter(wl[2])))

    return scores

def insertInto(line, cur, conn):
    cur.execute("SELECT id FROM Teams WHERE Abbreviation = ?", (line[1],))
    tid = int(cur.fetchone()[0])
    conn.commit()

    cur.execute('''SELECT Date FROM Winners WHERE Date = ? AND Team_id = ?''', (line[0], tid))
    if len(cur.fetchall()) > 0:
        print("This winner between " + line[1] + " and " + line[2] + " is already in the database.")
    else:
        cur.execute("INSERT INTO Winners (Date, Team_id) VALUES (?, ?)", (line[0], tid))
        print(line[1] + " beating " + line[2] + " added to the database!")
    conn.commit()

def winloseTable(scores):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path +'/'+'stats.db')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS Winners (Date TEXT, Team_id INTEGER)''')
    conn.commit()

    for i in scores:
        insertInto(i, cur, conn)

    combiner(cur, conn)

def combiner(cur, conn):
    dataList = []
    cur.execute('''SELECT * FROM Team_Stats INNER JOIN AdvStats ON Team_Stats.Team_id = AdvStats.Team_id AND Team_Stats.Last_updated = AdvStats.Date
                INNER JOIN Moneylines ON AdvStats.Team_id = Moneylines.Team_id AND AdvStats.Date = Moneylines.Date INNER JOIN Winners 
                ON Moneylines.Date = Winners.Date AND (Moneylines.Team_id = Winners.Team_id OR Moneylines.Opponent_id = Winners.Team_id)''')
    for i in cur:
        home = 0
        if i[22] == "Yes":
            home = 1
        winner = 0
        if i[57] == i[0]:
            winner = 1
        dataList.append([i[8], i[0], home, i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[11], i[12], i[13], i[14], i[15], i[16], i[17], i[18], i[19], i[23], winner])
    modelDat = []
    for j in dataList:
        cur.execute('''SELECT * FROM Team_Stats INNER JOIN AdvStats ON Team_Stats.Team_id = AdvStats.Team_id AND Team_Stats.Last_updated = AdvStats.Date WHERE Team_Stats.Team_id = ? AND Team_Stats.Last_updated = ?''', (j[19], j[0]))
        add = j
        oppStats = cur.fetchone()
        nums = [1, 2, 3, 4, 5, 6, 7, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        for k in range(0, len(oppStats)):
            if k in nums:
                add.append(oppStats[k])
        modelDat.append(add)
    
    return modelDat



    print(dataList)

def fullJob():
    winloseTable(winFinder())
    print("Database updated.")

if __name__ == "__main__":
    fullJob()

