from bs4 import BeautifulSoup
import requests
import os
import json
import sqlite3
from datetime import date


def statFinder():
    url = "http://www.espn.com/nba/hollinger/teamstats"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    outer = soup.find('table', class_="tablehead")
    trs = outer.find_all('tr')

    data = []

    for i in range(2, len(trs)):
        guy = trs[i]
        team = guy.find('a').text
        stats = guy.find_all('td')
        pace = stats[2].text
        to = stats[4].text
        orr = stats[5].text
        drr = stats[6].text
        rebr = stats[7].text
        efg = stats[8].text
        ts = stats[9].text
        offef = stats[10].text
        defef = stats[11].text
        data.append((team, pace, to, orr, drr, rebr, efg, ts, offef, defef))

    return data

def teamConvert(team):
    teams = {
        "LA Clippers": "LAC",
        "Brooklyn": "BKN",
        "Utah": "UTAH",
        "Denver": "DEN",
        "Milwaukee": "MIL",
        "Phoenix": "PHX",
        "Portland": "POR",
        "Atlanta": "ATL",
        "Dallas": "DAL",
        "New Orleans": "NO",
        "Sacramento": "SAC",
        "Boston": "BOS",
        "Memphis": "MEM",
        "Philadelphia": "PHI",
        "Toronto": "TOR",
        "Chicago": "CHI",
        "Indiana": "IND",
        "Charlotte": "CHA",
        "San Antonio": "SAS",
        "Golden State": "GSW",
        "LA Lakers": "LAL",
        "New York": "NYK",
        "Washington": "WAS",
        "Miami": "MIA",
        "Detroit": "DET",
        "Minnesota": "MIN",
        "Houston": "HOU",
        "Orlando": "ORL",
        "Cleveland": "CLE",
        "Oklahoma City": "OKC"
    }

    return teams[team]

def tabMaker(cur, conn):
    cur.execute('''CREATE TABLE IF NOT EXISTS AdvStats (Date TEXT, Team_id INTEGER, Pace REAL,
    TurnoverRatio REAL, OffRebRate REAL, DefRebRate REAL, RebRate REAL, EffFGPerc REAL, TrueSP REAL,
    OffEff REAL, DefEff REAL)''')
    conn.commit()

def tabAddition(cur, conn, line):
    cur.execute("SELECT id FROM Teams WHERE Abbreviation = ?", (teamConvert(line[0]),))
    tid = int(cur.fetchone()[0])
    cur.execute('''INSERT INTO AdvStats (Date, Team_id, Pace, TurnoverRatio, OffRebRate, DefRebRate,
            RebRate, EffFGPerc, TrueSP, OffEff, DefEff) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (str(date.today()), tid, line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8], line[9]))
    conn.commit()

def Printer(lines):
    print("TEAM       PACE TORat OffRebRate DefRebRate EffFGPerc TrueSP OffEff DefEff")
    for i in lines:
        print(i[0] + " " + str(i[1]) + " " + str(i[2]) + " " + str(i[3]) + " " + str(i[4]) + " " + str(i[5]) + " " + str(i[6]) + " " + str(i[7]) + " " + str(i[8]) + " " + str(i[9]))
    print("Advanced Stats as of " + str(date.today()))

if __name__ == "__main__":
    data = statFinder()
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'stats.db')
    cur = conn.cursor()
    tabMaker(cur, conn)
    for i in data:
        tabAddition(cur, conn, i)
    Printer(data)
    print("Advanced Data added to database")

