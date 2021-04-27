from bs4 import BeautifulSoup
import requests
import os
import json
import sqlite3
from datetime import date

def askDate():
    x = input("Please enter a date in YYYYmmdd format (Ex. 20210426): ")
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


def fullJob():
    winloseTable(winFinder())
    print("Database updated.")

if __name__ == "__main__":
    fullJob()

