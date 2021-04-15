import json
import os
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import date

path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+'stats.db')
cur = conn.cursor()

def team_abrevs():
    abrevs = {}
    wiki = requests.get("https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Basketball_Association/National_Basketball_Association_team_abbreviations")
    soup = BeautifulSoup(wiki.text, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')
    for x in range(1, len(rows)):
        row = rows[x]
        names = row.find_all('td')
        abr = names[0].text
        abr = abr.strip()
        team = names[1].text
        team = team.strip()
        abrevs[team] = abr
    abrevs['New Orleans Pelicans'] = 'NO'
    abrevs['Utah Jazz'] = 'UTAH'
    return abrevs

def get_team_stats(team):
    output = {}
    cur.execute(f"SELECT * FROM Teams where Team = '{team}'")
    ab = ""
    ident = 0
    for row in cur:
        ab = row[2]
        ident = row[0]
    output['Team'] = team
    output['Abbreviation'] = ab
    url = f"https://www.espn.com/nba/team/_/name/{ab}/{team}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    column = soup.find('section', class_ = "col-c chk-height")
    sections = column.find_all('article')

    stats = sections[3]
    blocks = stats.find_all('div')
    for x in range(1,5):
        first = blocks[x].find_all('span')
        category = first[0].text
        value = first[1].text
        output[category] = value

    stats = column.find('article', class_ = "sub-module teamseasonhistory")
    blocks = stats.find_all('td')
    w = blocks[1].text
    l = blocks[2].text
    output['Wins'] = w
    output['Losses'] = l
    
    column = soup.find('section', class_ = "col-a chk-height")
    games = column.find_all('li')
    last_10 = []
    for x in range(1, 11):
        results = games[x].find_all('div')
        res = results[3].text
        last_10.append(res)
    w = 0
    for res in last_10:
        if res == 'W':
            w += 1
    win_per = w/10
    output['Last 10 Win Percentage'] = win_per
    return output

def stats(team):
    cur.execute(f'SELECT * FROM Teams WHERE Team = "{team}"')
    result = cur.fetchone()
    if result:
        ident = result[0]
        ab = result[2]
    else:
        print("team not found")
        return
    cur.execute('CREATE TABLE IF NOT EXISTS Team_Stats (Team_id INTEGER, PPG REAL, RPG REAL, APG REAL, Points_Allowed REAL, Wins INTEGER, Losses INTEGER, Last_10_Win_Percentage REAL, Last_updated TEXT)')
    cur.execute(f"SELECT * FROM Team_Stats WHERE Team_id = '{ident}'")
    result = cur.fetchone()
    now = date.today()
    now = str(now)
    if result and result[8] == now:
        val = {}
        val['Team'] = team
        val['Abbreviation'] = ab
        val['Points Per Game'] = result[1]
        val['Rebounds Per Game'] = result[2]
        val['Assists Per Game'] = result[3]
        val['Points Allowed'] = result[4]
        val['Wins'] = result[5]
        val['Losses'] = result[6]
        val['Last 10 Win Percentage'] = result[7]
        return val
    if result and result[8] != now:
        val = get_team_stats(team)
        cur.execute(f"UPDATE Team_Stats SET PPG = '{val['Points Per Game']}', RPG = '{val['Rebounds Per Game']}', APG = '{val['Assists Per Game']}', Points_Allowed = '{val['Points Allowed']}', Wins = '{val['Wins']}', Losses = '{val['Losses']}', Last_updated = '{now}' WHERE Team_id = '{ident}'")
        conn.commit()
        return val
    if not result:
        val = get_team_stats(team)
        cur.execute("INSERT INTO Team_Stats (Team_id, PPG, RPG, APG, Points_Allowed, Wins, Losses, Last_10_Win_Percentage, Last_updated) VALUES (?,?,?,?,?,?,?,?,?)",
        (ident, val['Points Per Game'], val['Rebounds Per Game'], val['Assists Per Game'], val['Points Allowed'], val['Wins'], val['Losses'], val['Last 10 Win Percentage'], now))
        conn.commit()
        return val

def make_id_table():
    abrevs = team_abrevs()
    cur.execute('CREATE TABLE IF NOT EXISTS Teams (id INTEGER PRIMARY KEY, Team TEXT, Abbreviation TEXT)')
    cur.execute("SELECT * FROM Teams")
    result = cur.fetchone()
    if result:
        return
    for key in abrevs:
        cur.execute('INSERT INTO Teams (Team, Abbreviation) VALUES (?, ?)', (key, abrevs[key]))
    conn.commit()


make_id_table()







