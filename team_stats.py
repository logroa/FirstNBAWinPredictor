import json
import os
import requests
from bs4 import BeautifulSoup
import sqlite3

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
    return abrevs

def get_team_stats(team):
    abrevs = team_abrevs()
    output = {}
    output['Team'] = team
    output['Abbreviation'] = abrevs[team]
    url = f"https://www.espn.com/nba/team/_/name/{abrevs[team]}/{team}"
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

    stats = sections[7]
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
    cur.execute('CREATE TABLE IF NOT EXISTS Team_Stats (Team TEXT, Abbreviation TEXT, PPG INTEGER, RPG INTEGER, APG INTEGER, Points_Allowed INTEGER, Wins INTEGER, Losses INTEGER, Last_10_Win_Percentage REAL)')
    cur.execute(f"SELECT * FROM Team_Stats where Team = '{team}'")
    result = cur.fetchone()
    if result:
        val = {}
        val['Team'] = result[0]
        val['Abbreviation'] = result[1]
        val['Points Per Game'] = result[2]
        val['Rebounds Per Game'] = result[3]
        val['Assists Per Game'] = result[4]
        val['Points Allowed'] = result[5]
        val['Wins'] = result[6]
        val['Losses'] = result[7]
        val['Last 10 Win Percentage'] = result[8]
        return val
    else:
        val = get_team_stats(team)
        cur.execute("INSERT INTO Team_Stats (Team, Abbreviation, PPG, RPG, APG, Points_Allowed, Wins, Losses, Last_10_Win_Percentage) VALUES (?,?,?,?,?,?,?,?,?)",
        (val['Team'], val['Abbreviation'], val['Points Per Game'], val['Rebounds Per Game'], val['Assists Per Game'], val['Points Allowed'], val['Wins'], val['Losses'], val['Last 10 Win Percentage']))
        conn.commit()
        return val

def make_id_table():
    abrevs = team_abrevs()
    cur.execute('CREATE TABLE IF NOT EXISTS Teams (id INTEGER PRIMARY KEY, Team TEXT, Abbreviation TEXT)')
    for key in abrevs:
        cur.execute('INSERT INTO Teams (Team, Abbreviation) VALUES (?, ?)', (key, abrevs[key]))
    conn.commit()

print(stats("Oklahoma City Thunder"))








