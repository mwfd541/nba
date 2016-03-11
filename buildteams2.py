import pandas as pd
from scipy.optimize import linprog
import numpy as np

LowerSalaryBound = 4100

runs = 300
Tune_1 =3
Tune_2	= 1
eta = .5 #it appear from playing around the .5 generates the most teams 

current = pd.read_csv('current.csv')

current = pd.get_dummies(current, columns = ['Position'])

print current
df = pd.read_csv('today.csv')
df = pd.merge(df, current, on = ['Id','Salary','Team'], how = 'left')
#df['Full Name']=df['First Name']+' '+df['Last Name']

print df

for x in df.index:
	if(df.Salary.iloc[x]<LowerSalaryBound):
		df.FDexpected.iloc[x]=0


df['Injured']=np.zeros(len(df.index))
df.InjuryIndicator=df['Injury Indicator'].fillna(0)  
for h in df.index:
	if df.InjuryIndicator[h] !=0 : df.Injured[h]=1
	

f=-df.FDexpected

class Team(object):
	def __init__(self, dtf):
		self.dtfr=dtf
		self.salary=dtf.Salary.sum()
		self.homecourt=dtf.home_court.sum()
		self.expt=dtf.FPPG.sum()
		self.ws=dtf.weighted.sum()/100
	

PG=list(df.Position_PG)
PF=list(df.Position_PF)
SF=list(df.Position_SF)
SG=list(df.Position_SG)
C=list(df.Position_C)
Inj=list(df.Injured)

Sal=list(df.Salary)

A=[Sal,PG,PF,SF,SG,C,Inj]
x0_bounds = (0, 1)
teamlist=[]


print A
print f

print PG
for p in range(runs):
	ff=f-Tune_1*np.random.randn(len(f))
	B=[60000+Tune_2*1000*np.random.randn(),2,2,2,2,1,0.0001]
	print B

	res = linprog(ff, A_ub=A, b_ub=B, bounds=(x0_bounds),options={"disp": False})
	draft=res.x-eta
	draft = np.ceil(draft)
	print draft
	print draft.dot(PG)
	print draft.dot(PF)
	if draft.dot(Sal)<60001:
			print draft.dot(Sal)
			if (draft.sum()==9):
				print '\n'
				print 'found team'
				print draft
				teamlist = teamlist +[draft]
				print len(teamlist)
			else : print 'too small', draft.sum()
	else : print 'too pricey',draft.dot(Sal)
teamdf = pd.DataFrame(teamlist)
print 'we got', len(teamlist), 'teams'
teamdf.to_csv('teams.csv')
				
				
				
#Now add the standard deviation to the today2 file



gamelog = pd.read_csv('2015games.csv')
gamelog['FanDuel']=2*gamelog['FGM']+gamelog['FG3M']+gamelog['FTM']+1.2*gamelog['REB']+1.5*gamelog['AST']+2*gamelog['BLK']+2*gamelog['STL']-gamelog['TOV']
lmean = gamelog.groupby(['PLAYER_NAME'])['FanDuel'].mean()
lvar = gamelog.groupby(['PLAYER_NAME'])['FanDuel'].std()
lvar = pd.DataFrame(lvar)
lvar['PLAYER_NAME']=lvar.index
lvar.rename(columns={'FanDuel':'sigma'}, inplace=True)
lvar.to_csv('today3.csv')

today = pd.read_csv('today.csv')
today['PLAYER_NAME']=today['First Name']+' '+today['Last Name']

today2 = pd.merge(today, lvar, on = ['PLAYER_NAME'], how = 'left')
today2.to_csv('today2.csv')