
import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
import xgboost as xgb
import datetime


TODAY = datetime.datetime.today()
print "today's date is ",  TODAY.strftime("%m%d")



STOPPING = 200
BOOST = 10000

## Start of main script
train = pd.read_csv("train2.csv")
test = pd.read_csv("test2.csv")
#ids=test[['PLAYER_ID','PLAYER_NAME']]

train.fillna(-1,inplace=True, downcast = 'infer')  
test.fillna(-1,inplace=True, downcast = 'infer')

team_dummies = [c for c in test.columns.values if 'Opponent_' in c]
player_dummies =  [c for c in test.columns.values if 'PLAYER_ID_' in c]
position_dummies = [c for c in test.columns.values if 'Position_' in c ]
player_dummies.remove('PLAYER_ID_0')  # this shows up in test but not in train
other14_features = test.columns.values[26:46]

train.MIN = train.MIN.replace(0,0.5)
train.FanDuel = train.FanDuel.fillna(0.0)
train['fd_per_minute'] = train.FanDuel.divide(train.MIN,fill_value = 0.0) 


features_test = team_dummies+player_dummies+position_dummies+['home','away','rest','recent_minutes','AGE']+list(other14_features)+['sum1','sum2','historicalSal']

features_train =features_test 
features = features_train



def rmspe(y, yhat):
	print (y.min())
	s = pd.Series(y,yhat)
	ret = np.sqrt(np.mean(((y - yhat)) ** 2))
	#print(s)
	return ret

def rmspe_xg(yhat, y):
    y = y.get_label()
   
    return "rmspe", rmspe(y, yhat)
	
## STEP 1 is the classic, more straightforward one.  


params = {"objective": "reg:linear",
          "booster" : "gbtree",
          "eta": 0.025,
          "max_depth": 3,
          "subsample": 0.85,
          "colsample_bytree": 0.4,
          "min_child_weight": 4,
          "silent": 1,
          "thread": 1,
          "seed": 541
          }
num_boost_round = BOOST

X_train, X_valid = train_test_split(train, test_size=0.12, random_state=15)
y_train = X_train.FanDuel
y_valid = X_valid.FanDuel
dtrain = xgb.DMatrix(X_train[features_train], y_train)
dvalid = xgb.DMatrix(X_valid[features_train], y_valid)

watchlist = [(dtrain, 'train'), (dvalid, 'eval')]
gbm = xgb.train(params, dtrain, num_boost_round, evals=watchlist, early_stopping_rounds=STOPPING, \
  feval=rmspe_xg, verbose_eval=True)

print("Validating")
yhat = gbm.predict(xgb.DMatrix(X_valid[features_train]))
error = rmspe(X_valid.FanDuel.values, yhat)
print('RMSPE: {:.6f}'.format(error))

print("Make predictions on the test set")
dtest = xgb.DMatrix(test[features_test])
test_probs = gbm.predict(dtest)
result = pd.DataFrame({"Id": test["Id"], 'FanDuel1': test_probs, 'First Name': test['First Name'], 'Last Name' : test['Last Name'], 'FPPG_historical' : test['FPPG'], 'Salary': test['Salary'], 'Team': test['Team']})

# STEP two, we predict minutes

## first expected FanDuel per minute ######################
X_train, X_valid = train_test_split(train, test_size=0.12, random_state=12)
y_train = X_train.fd_per_minute
y_valid = X_valid.fd_per_minute
print(len(y_valid))
dtrain = xgb.DMatrix(X_train[features_train], y_train)
dvalid = xgb.DMatrix(X_valid[features_train], y_valid)

watchlist = [(dtrain, 'train'), (dvalid, 'eval')]
gbm = xgb.train(params, dtrain, num_boost_round, evals=watchlist, early_stopping_rounds=STOPPING, \
  feval=rmspe_xg, verbose_eval=True)

yhat = gbm.predict(xgb.DMatrix(X_valid[features_train]))
error = rmspe(X_valid.fd_per_minute.values, yhat)
print('RMSPE: {:.6f}'.format(error))

dtest = xgb.DMatrix(test[features_test])
test_probs = gbm.predict(dtest)
result['fd_per_minute']= test_probs

## next expected minutes ######################
X_train, X_valid = train_test_split(train, test_size=0.12, random_state=12)
y_train = X_train.MIN
y_valid = X_valid.MIN
print(len(y_valid))
dtrain = xgb.DMatrix(X_train[features_train], y_train)
dvalid = xgb.DMatrix(X_valid[features_train], y_valid)

watchlist = [(dtrain, 'train'), (dvalid, 'eval')]
gbm = xgb.train(params, dtrain, num_boost_round, evals=watchlist, early_stopping_rounds=STOPPING, \
  feval=rmspe_xg, verbose_eval=True)

yhat = gbm.predict(xgb.DMatrix(X_valid[features_train]))
error = rmspe(X_valid.MIN.values, yhat)
print('RMSPE: {:.6f}'.format(error))

dtest = xgb.DMatrix(test[features_test])
test_probs = gbm.predict(dtest)
result['MINexpected'] =test_probs
result['FDexpected'] = result.MINexpected*result.fd_per_minute
error = rmspe(X_valid.MIN.values, yhat)
print (result.head(10))


#Next, stats separately 



filename = TODAY.strftime("%m%d")+'.csv'
result.to_csv(filename)

result.to_csv('today.csv')

