import requests
import json

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


if __name__ == "__main__":
    name = input("Enter a team name with capitalized first letters and the city (ex. Washington Wizards): ")
    siteList = odds_finder(name)
    if siteList != None:
        oddsList = []
        for i in siteList:
            oddsList.append((i[0], i[1], winPercCalc(i[1]), i[2], i[3]))
        outputter(name, oddsList)