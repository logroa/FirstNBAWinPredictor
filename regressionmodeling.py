# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as mp
import seaborn as sb
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, plot_confusion_matrix, precision_recall_curve, plot_precision_recall_curve, plot_roc_curve

df = pd.read_csv("modelData.csv")

df = df.drop('date', 1)

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