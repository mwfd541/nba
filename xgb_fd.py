
#from __future__ import print_function
import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
import xgboost as xgb



## Start of main script
train = pd.read_csv("train.csv")
test = pd.read_csv("test.csv")
#ids=test[['PLAYER_ID','PLAYER_NAME']]

test.fillna(111, inplace=True)

features_train = train.columns[51:56]
features_test = test.columns[-5:]
team_dummies = [c for c in test.columns.values if 'Opponent_' in c]
player_dummies =  [c for c in test.columns.values if 'PLAYER_ID_' in c]
position_dummies = [c for c in test.columns.values if 'Position_' in c ]
player_dummies.remove('PLAYER_ID_0')  # this shows up in test but not in train
other14_features = test.columns.values[26:46]

features_test = team_dummies+player_dummies+position_dummies+['home','away','rest','recent_minutes','AGE']+list(other14_features)

features_train =features_test 



print('training data processed')
def rmspe(y, yhat):
	print (y.min())
	s = pd.Series(y,yhat)
	ret = np.sqrt(np.mean(((y - yhat)) ** 2))
	#print(s)
	return ret

def rmspe_xg(yhat, y):
    y = y.get_label()
   
    return "rmspe", rmspe(y, yhat)

print("Train xgboost model")

params = {"objective": "reg:linear",
          "booster" : "gbtree",
          "eta": 0.003,
          "max_depth": 9,
          "subsample": 0.85,
          "colsample_bytree": 0.4,
          "min_child_weight": 4,
          "silent": 1,
          "thread": 1,
          "seed": 104
          }
num_boost_round = 10000

print("Train a XGBoost model")
X_train, X_valid = train_test_split(train, test_size=0.12, random_state=12)
y_train = X_train.FanDuel
y_valid = X_valid.FanDuel
print(len(y_valid))
dtrain = xgb.DMatrix(X_train[features_train], y_train)
dvalid = xgb.DMatrix(X_valid[features_train], y_valid)

watchlist = [(dtrain, 'train'), (dvalid, 'eval')]
gbm = xgb.train(params, dtrain, num_boost_round, evals=watchlist, early_stopping_rounds=200, \
  feval=rmspe_xg, verbose_eval=True)

print("Validating")
yhat = gbm.predict(xgb.DMatrix(X_valid[features_train]))
error = rmspe(X_valid.FanDuel.values, yhat)
print('RMSPE: {:.6f}'.format(error))

print("Make predictions on the test set")
dtest = xgb.DMatrix(test[features_test])
test_probs = gbm.predict(dtest)
# Make Submission
result = pd.DataFrame({"Id": test["Id"], 'FanDuel': test_probs, 'FPPG_historical' : test['FPPG'], 'Salary': test['Salary'], 'Team': test['Team']})
#result = pd.merge(result, ids, on='PLAYER_ID', how='left')
print (result.head(10))

result.to_csv("nbapred.csv", index=False)

