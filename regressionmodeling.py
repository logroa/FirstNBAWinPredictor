# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as mp
import seaborn as sb
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import sqlite3
import os
from datetime import date
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, plot_confusion_matrix, precision_recall_curve, plot_precision_recall_curve, plot_roc_curve

def modelMaker(specTeam):
    df = pd.read_csv("modelData.csv")
    todayGames = pd.read_csv("todayData.csv")
    
    df = df.drop('date', 1)
    todayGames = todayGames.drop('date', 1)
    
    y = df[['win']]
    X = df.drop('win', 1)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.5, random_state=101)
    
    logreg = LogisticRegression(max_iter=1000)
    logreg.fit(X_train, y_train)
    LogisticRegression()
    
    odds = np.exp(logreg.coef_)
    
    print("Odd Ratios: ")
    list1 = list(X)
    list2 = list(odds)
    for i in range(0, len(list1)):
        print(list1[i] + ": " + str(list2[0][i]))
    
    
    predictions = logreg.predict(X_test)
    print(classification_report(y_test, predictions))
    print("Accuracy Score: ", accuracy_score(y_test, predictions))
    confusion_matrix(y_test, predictions)
    
    plot_confusion_matrix(logreg, X_test, y_test, normalize='true')
    plot_roc_curve(logreg, X_test, y_test)
    
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/' + 'stats.db')
    cur = conn.cursor()
    
    cur.execute("SELECT id FROM Teams WHERE Team = ?", (specTeam,))
    tid = cur.fetchone()[0]
    tW = 0
    
    print("Today's Predictions: ")
    todayPred = logreg.predict(todayGames)
    todayGames['winPred'] = todayPred
    for key, i in todayGames.iterrows():
        if i['team_id'] == tid:
            tW = i['winPred']
        cur.execute("SELECT Team FROM Teams WHERE id = ?", (i['team_id'],))
        tname = cur.fetchone()[0]
        cur.execute("SELECT Team FROM Teams WHERE id = ?", (i['opponent_id'],))
        oname = cur.fetchone()[0]
        word = ""
        if i['winPred'] == 0:
            word = "not "
        print(tname + " are " + word + "projected to beat " + oname + " today.")
    
    print("")
    
    cur.execute("SELECT * FROM Moneylines WHERE Team_id = ? AND Date = ?", (tid, str(date.today())))
    lines = cur.fetchall()[0]
    avg = 0
    count = 0
    for i in range(5, len(lines), 2):
        count += 1
        avg += lines[i]
    avg = avg/count
    print("Average Vegas calculated win percentage for " + specTeam + " today is " + str(avg) + ",")
    if tW == 1 and avg <= 50:
        print("there may be value in looking into this moneyline bet")
    elif tW == 1 and avg > 50:
        print("this is likely the expected outcome where the favorite, your selected team, will win")
    elif tW == 0 and avg <= 50:
        print("this is likely the expected outcome where the favorite, your selected team's opponent, will win")
    else:
        print("there may be value in looking into betting moneyline against your selected team")
    print("based on our predictions.")
    
if __name__ == "__main__":
    modelMaker("Golden State Warriors")
    