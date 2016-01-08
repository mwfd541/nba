
import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
import xgboost as xgb
import datetime


TODAY = datetime.datetime.today()
print "today's date is ",  TODAY.strftime("%m%d")



STOPPING = 100
BOOST = 50000

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

train.MIN = train.MIN.replace(0,0.5)
train.FanDuel = train.FanDuel.fillna(0.0)
train['fd_per_minute'] = train.FanDuel.divide(train.MIN,fill_value = 0.0) 


features_test = team_dummies+player_dummies+position_dummies+['home','away','rest','recent_minutes','AGE']+list(other14_features)

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
          "eta": 0.003,
          "max_depth": 9,
          "subsample": 0.85,
          "colsample_bytree": 0.4,
          "min_child_weight": 4,
          "silent": 1,
          "thread": 1,
          "seed": 18904
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

params = {"objective": "reg:linear",
          "booster" : "gbtree",
          "eta": 0.008,
          "max_depth": 9,
          "subsample": 0.85,
          "colsample_bytree": 0.4,
          "min_child_weight": 5,
          "silent": 1,
          "thread": 1,
          "seed": 11126
          }
num_boost_round = BOOST

statlist = ['FGM',	'FG3M',	'FTM','REB','AST','BLK','STL','TOV']

def stattrain(s):
	print("Train a XGBoost model", s)
	X_train, X_valid = train_test_split(train, test_size=0.14, random_state=10)
	y_train = X_train[s].fillna(0)
	print (y_train)
	y_valid = X_valid[s].fillna(0)
	dtrain = xgb.DMatrix(X_train[features], y_train)
	dvalid = xgb.DMatrix(X_valid[features], y_valid)
	watchlist = [(dtrain, 'train'), (dvalid, 'eval')]
	gbm = xgb.train(params, dtrain, num_boost_round, evals=watchlist, early_stopping_rounds=STOPPING, feval=rmspe_xg, verbose_eval=True)
	print("Validating")
	yhat = gbm.predict(xgb.DMatrix(X_valid[features]))
	error = rmspe(X_valid.FanDuel.values, yhat)
	print('RMSPE: {:.6f}'.format(error))
	print("Make predictions on the test set")
	dtest = xgb.DMatrix(test[features])
	test_probs = gbm.predict(dtest)
	result = pd.DataFrame({"PLAYER_ID": test["PLAYER_ID"], s: test_probs})
	return result

ids=test[['PLAYER_ID','Last Name']]
pred_df = ids
for s in statlist:
	a= stattrain(s)
	pred_df = pd.merge(pred_df, a, on ='PLAYER_ID',how = 'left')
	

pred_df ['FanDuel']=2*pred_df ['FGM']+pred_df ['FG3M']+pred_df ['FTM']+1.2*pred_df ['REB']+1.5*pred_df ['AST']+2*pred_df ['BLK']+2*pred_df ['STL']-pred_df ['TOV']
result['statspred']=pred_df ['FanDuel']



# finally, we do a lower and a higher pred

def rmspeW(y, yhat, PLUS, MINUS):
	diff = y - yhat
	over = np.maximum(diff, 0)
	under = np.maximum(-diff, 0)
	weighted = PLUS*over + MINUS*under
	ret = np.sqrt(np.mean((weighted) ** 2))
	return ret
	

def rmspe_xgH(yhat, y):
    y = y.get_label()
   
    return "rmspe", rmspeW(y, yhat, 1, 1.7)

def rmspe_xgL(yhat, y):
    y = y.get_label()
   
    return "rmspe", rmspeW(y, yhat, 1.7, 1.0)
	


params = {"objective": "reg:linear",
          "booster" : "gbtree",
          "eta": 0.008,
          "max_depth": 9,
          "subsample": 0.85,
          "colsample_bytree": 0.4,
          "min_child_weight": 5,
          "silent": 1,
          "thread": 1,
          "seed": 19726
          }
num_boost_round = BOOST
X_train, X_valid = train_test_split(train, test_size=0.14, random_state=9)
y_train = X_train.FanDuel
y_valid = X_valid.FanDuel
print(len(y_valid))
dtrain = xgb.DMatrix(X_train[features_train], y_train)
dvalid = xgb.DMatrix(X_valid[features_train], y_valid)

watchlist = [(dtrain, 'train'), (dvalid, 'eval')]
gbm = xgb.train(params, dtrain, num_boost_round, evals=watchlist, early_stopping_rounds=STOPPING, \
  feval=rmspe_xgH, verbose_eval=True)

print("Validating")
yhat = gbm.predict(xgb.DMatrix(X_valid[features_train]))
error = rmspeW(X_valid.FanDuel.values, yhat, 1.0, 1.7)
print('RMSPE: {:.6f}'.format(error))

print("Make predictions on the test set")
dtest = xgb.DMatrix(test[features_test])
test_probs = gbm.predict(dtest)

result['punishlower'] = test_probs

##  And the other side 

params = {"objective": "reg:linear",
          "booster" : "gbtree",
          "eta": 0.008,
          "max_depth": 9,
          "subsample": 0.85,
          "colsample_bytree": 0.4,
          "min_child_weight": 5,
          "silent": 1,
          "thread": 1,
          "seed": 16
          }
num_boost_round = BOOST
X_train, X_valid = train_test_split(train, test_size=0.14, random_state=11)
y_train = X_train.FanDuel
y_valid = X_valid.FanDuel
print(len(y_valid))
dtrain = xgb.DMatrix(X_train[features_train], y_train)
dvalid = xgb.DMatrix(X_valid[features_train], y_valid)

watchlist = [(dtrain, 'train'), (dvalid, 'eval')]
gbm = xgb.train(params, dtrain, num_boost_round, evals=watchlist, early_stopping_rounds=STOPPING, \
  feval=rmspe_xgL, verbose_eval=True)

print("Validating")
yhat = gbm.predict(xgb.DMatrix(X_valid[features_train]))
error = rmspeW(X_valid.FanDuel.values, yhat, 1.0, 1.7)
print('RMSPE: {:.6f}'.format(error))

print("Make predictions on the test set")
dtest = xgb.DMatrix(test[features_test])
test_probs = gbm.predict(dtest)

result['punishhigher'] = test_probs








filename = TODAY.strftime("%m%d")+'.csv'
result.to_csv(filename)

