import requests
import json
import sqlite3
from datetime import date
import os

def odds_finder(team_name):
    url = "https://odds.p.rapidapi.com/v1/odds"

    querystring = {"sport":"basketball_nba","region":"us","mkt":"h2h","dateFormat":"iso","oddsFormat":"american"}

    headers = {
        'x-rapidapi-key': "275189ae59mshe64ed3181a235dcp122fabjsn5cf4e3c2ac01",
        'x-rapidapi-host': "odds.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    data = json.loads(response.text)

    
    if data['success'] == False:
        print("Unsuccessful Initial Request")
        return None
    
    list1 = data['data']
    playToday = False
    homeTeam = False
    for i in list1:
        if team_name in i['teams']:
            playToday = True
            if team_name == i['home_team']:
                homeTeam = True
            if team_name == i['teams'][0]:
                oddInd = 0
                opponent = i['teams'][1]
            if team_name == i['teams'][1]:
                oddInd = 1
                opponent = i['teams'][0]
            break
    if playToday == True:
        outputOdds = []
        for j in i['sites']:
            name = j['site_nice']
            odd = j['odds']['h2h'][oddInd]
            home = "No"
            if homeTeam == True:
                home = "Yes"
            outputOdds.append((name, odd, home, opponent))
        return outputOdds
    else:
        print("Specified team not playing today.")
        return None

def winPercCalc(num):
    if num < 0:
        num *= -1
        perc = float(num/(num+100))
    else:
        perc = float(100/(100+num))
    return round(perc*100, 2)

def outputter(name, outputList):
    print(name + ", Home Team: " + outputList[0][3] + "; Opponent: " + outputList[0][4])
    print("BOOK    ODDS    WINNING PERCENTAGE")
    for i in outputList:
        print(i[0] + " " + str(i[1]) + " " + str(i[2]))

def dbMaker(cur, conn):
    cur.execute('''CREATE TABLE IF NOT EXISTS Moneylines (Date TEXT, Team_id INTEGER, HomeTeam TEXT, Opponent_id INTEGER, oddsFANDUEL INTEGER,
                winpercFANDUEL REAL, oddsFOXBET INTEGER, winpercFOXBET REAL, oddsBOVADA INTEGER, winpercBOVADA REAL, 
                oddsUNIBET INTEGER, winpercUNIBET REAL, oddsBETRIVERS INTEGER, winpercBETRIVER REAL, oddsDRAFTKINGS INTEGER,
                winpercDRAFTKINGS REAL, oddsSUGARHOUSE INTEGER, winpercSUGARHOUSE REAL, oddsPOINTSBET INTEGER, winpercPOINTSBET REAL,
                oddsBETFAIR INTEGER, winpercBETFAIR REAL, oddsBETONLINE INTEGER, winpercBETONLINE REAL, oddsWILLIAMHILL INTEGER,
                winpercWILLIAMHILL REAL, oddsINTERTOPS INTEGER, winpercINTERTOPS REAL, oddsGTBETS INTEGER, winpercGTBETS REAL,
                oddsBOOKMAKER INTEGER, winpercBOOKMAKER REAL, oddsMYBOOKIE INTEGER, winpercMYBOOKIE REAL, oddsCAESARS INTEGER,
                winpercCAESARS REAL)''')
    conn.commit()

def dbAddition(name, oL, cur, conn):
    cur.execute("SELECT id FROM Teams WHERE Team = ?", (name,))
    tid = int(cur.fetchone()[0])
    cur.execute("SELECT id FROM Teams WHERE Team = ?", (oL[0][4],))
    oid = int(cur.fetchone()[0])

    cur.execute('''INSERT INTO Moneylines (Date, Team_id, HomeTeam, Opponent_id, oddsFANDUEL, winpercFANDUEL, oddsFOXBET, winpercFOXBET, oddsBOVADA, 
                winpercBOVADA, oddsUNIBET, winpercUNIBET, oddsBETRIVERS, winpercBETRIVER, oddsDRAFTKINGS, winpercDRAFTKINGS, oddsSUGARHOUSE,
                winpercSUGARHOUSE, oddsPOINTSBET, winpercPOINTSBET, oddsBETFAIR, winpercBETFAIR, oddsBETONLINE, winpercBETONLINE, oddsWILLIAMHILL,
                winpercWILLIAMHILL, oddsINTERTOPS, winpercINTERTOPS, oddsGTBETS, winpercGTBETS, oddsBOOKMAKER, winpercBOOKMAKER, oddsMYBOOKIE, 
                winpercMYBOOKIE, oddsCAESARS, winpercCAESARS) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (str(date.today()), tid, oL[0][3], oid, 
                oL[0][1], oL[0][2], oL[1][1], oL[1][2], oL[2][1], oL[2][2], oL[3][1], oL[3][2], oL[4][1], oL[4][2], oL[5][1], oL[5][2], oL[6][1], oL[6][2],
                oL[7][1], oL[7][2], oL[8][1], oL[8][2], oL[9][1], oL[9][2], oL[10][1], oL[10][2], oL[11][1], oL[11][2], oL[12][1], oL[12][2], oL[13][1], oL[13][2],
                oL[14][1], oL[14][2], oL[15][1], oL[15][2]))
    conn.commit()
    print("Data added to database")


if __name__ == "__main__":
    name = input("Enter a team name with capitalized first letters and the city (ex. Washington Wizards): ")
    siteList = odds_finder(name)
    if siteList != None:
        oddsList = []
        for i in siteList:
            oddsList.append((i[0], i[1], winPercCalc(i[1]), i[2], i[3]))
        outputter(name, oddsList)
        path = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(path+'/'+'stats.db')
        cur = conn.cursor()
        dbMaker(cur, conn)
        dbAddition(name, oddsList, cur, conn)
