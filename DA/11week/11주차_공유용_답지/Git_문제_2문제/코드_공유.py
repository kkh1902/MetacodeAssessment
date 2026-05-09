# 라이브러리 및 데이터 불러오기

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
from sklearn.datasets import load_wine

from sklearn.model_selection import train_test_split, GridSearchCV

import matplotlib.pyplot as plt

wine = load_wine()

# feature로 사용할 데이터에서는 'target' 컬럼을 drop합니다.
# target은 'target' 컬럼만을 대상으로 합니다.
# X, y 데이터를 test size는 0.2, random_state 값은 42로 하여 train 데이터와 test 데이터로 분할합니다.

''' 코드 작성 바랍니다 '''

df = pd.DataFrame(data=wine.data, columns= wine.feature_names)
df['target'] = wine.target

X = df.drop('target', axis=1)
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= 0.2, random_state= 42)

####### A 작업자 작업 수행 #######

# Admin_branch에서 수정 진행

''' 코드 작성 바랍니다 '''

from sklearn.tree import DecisionTreeClassifier

param_grid = {
    "criterion" : ['gini', 'entropy'],
    "max_depth" : [2, 3, 4, 5], # Admin_branch에서 수정 진행
    "min_samples_split": [2, 5, 10], # Admin_branch에서 수정 진행
    "min_samples_leaf": [1, 2, 4]
}

clf_grid = DecisionTreeClassifier( random_state= 42 )

grid_search = GridSearchCV(clf_grid, param_grid, cv = 5)

grid_search.fit(X_train, y_train) # HyperParameter를 찾고, 이걸 가지고 fitting이 모두 수행

print("Best Hyper-parameter", grid_search.best_params_)
print("Best Score", grid_search.best_score_)

clf_best_model = grid_search.best_estimator_

importances = clf_best_model.feature_importances_ # Feature Importance를 계산

plt.figure(figsize = (20,6)) # Best model의 Feature Importance를  시각화

plt.bar(range(len(importances)), importances, width=0.3) # 막대 그래프 생성
plt.xlabel('Feature')
plt.ylabel('importances')
plt.title('Feature Importance')
plt.xticks(range(len(importances)), X.columns, rotation = 45)
plt.show()

####### B 작업자 작업 수행 - B 작업자 수행완료 #######

''' 코드 작성 바랍니다 '''

from xgboost import XGBClassifier # Xgboost

xgb_model = XGBClassifier(random_state=42)

params = {
    "max_depth" : [3, 5, 7, 9, 15],
    "learning_rate" : [0.1, 0.01, 0.001],
    "n_estimators": [50, 100, 200, 300]
}

grid_search = GridSearchCV(estimator=xgb_model, param_grid=params, cv=5, scoring='accuracy', n_jobs=-1)
grid_search.fit(X_train, y_train)

print("Best parameters:", grid_search.best_params_)
print("Best accuracy:" , grid_search.best_score_)

xgb_best_model = grid_search.best_estimator_

importances = xgb_best_model.feature_importances_

plt.figure(figsize= (20,6))

plt.bar(range(len(importances)), importances, width= 0.3)
plt.xlabel('Feature')
plt.ylabel('importance')
plt.title('Feature Importance')
plt.xticks(range(len(importances)), X.columns, rotation =45)
plt.show()