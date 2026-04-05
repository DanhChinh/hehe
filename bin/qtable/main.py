import numpy as np
from data import make_data_3
from qclass import RLTradingSystem
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


scaler, X_train, y_train, X_test, y_test, X_pred, y_pred = make_data_3()


# model1 = RLTradingSystem("knn", KNeighborsClassifier(), X_train, y_train, X_test, y_test)
model2 = RLTradingSystem("decision_tree", DecisionTreeClassifier(), X_train, y_train, X_test, y_test)
# model3 = RLTradingSystem("random_forest", RandomForestClassifier(), X_train, y_train, X_test, y_test)


model = model2
for i in range(len(X_pred)):
    x = X_pred[i]
    y_true = y_pred[i]

    pred, score = model.make_predict_proba(x)
    model.check_predict_proba(y_true)
    print(f"i: {i}, isTrue: {model.compare_history[-1]} Score: {score}  sum: {sum(model.score_history)}")


from matplotlib import pyplot as plt
plt.plot(np.cumsum(model.score_history))
plt.title("Model Score History")
plt.xlabel("Sample Index")
plt.ylabel("Score")
plt.show()
