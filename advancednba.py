from bs4 import BeautifulSoup
import requests
import os
import json


def statFinder():
    url = "https://www.nba.com/stats/teams/advanced/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    outer = soup.find('main', class_="stats-container")
    inner = outer.find('div', class_="stats-container__inner")
    row = inner.find('div', class_="row")
    col = row.find('div', class_="columns")
    ss = col.find('div', class_="stats-splits")
    nst = ss.find('nba-stat-table', class_="stats-table-next")
    nstd = ss.find('div', class_="nba-stat-table")
    nstdo = nstd.find('div', class_="nba-stat-table__overflow")
    tab = nstdo.find('table')
    tb = tab.find('tbody')

    print(tb)



if __name__ == "__main__":
    statFinder()
