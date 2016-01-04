import pandas as pd
from scipy.optimize import linprog
import numpy as np

current = pd.read_csv('current.csv')
df = pd.read_csv('nbapred.csv')
df = pd.merge(df, current, on = ['Id','Salary','Team'], how = 'left')
df['Full Name']=df['First Name']+' '+df['Last Name']


f=-df.FanDuel

df['PG']=np.zeros(len(f))

df['PF']=np.zeros(len(f))

df['C']=np.zeros(len(f))

df['SG']=np.zeros(len(f))

df['SF']=np.zeros(len(f))
df['Injured']=np.zeros(len(f))

df['home_court']=np.zeros(len(f))

df['opweakness']=np.zeros(len(f))

df['weighted']=np.zeros(len(f))
df.InjuryIndicator=df['Injury Indicator'].fillna(0)  
for h in df.index:
	if df.Position[h]=='PG': df.PG[h]=1
	if df.Position[h]=='PF': df.PF[h]=1
	if df.Position[h]=='SF': df.SF[h]=1
	if df.Position[h]=='SG': df.SG[h]=1
	if df.Position[h]=='C': df.C[h]=1
	if df.InjuryIndicator[h] !=0 : df.Injured[h]=1
	

class Team(object):
	def __init__(self, dtf):
		self.dtfr=dtf
		self.salary=dtf.Salary.sum()
		self.homecourt=dtf.home_court.sum()
		self.expt=dtf.FPPG.sum()
		self.ws=dtf.weighted.sum()/100
	


PG=list(df.PG)
PF=list(df.PF)
SF=list(df.SF)
SG=list(df.SG)
C=list(df.C)
Inj = list(df.Injured)


A=list(df.Salary)

A=[A,PG,PF,SF,SG,C,Inj]
x0_bounds = (0, 1)
teamlist=[]


starting_value = 25
value_to_beat = starting_value
for p in range(2500):
	ff=f-np.random.randn(len(f))
	B=[60000+5000*np.random.randn(),2,2,2,2,1,.01]

	res = linprog(ff, A_ub=A, b_ub=B, bounds=(x0_bounds),options={"disp": False})
	df['draft']=res.x
	team=df[df['draft']>0.5]
	if team.Salary.sum()<60001:
		if team.FanDuel.sum()>value_to_beat:
			if (len(team)==9):
				print '\n'
				print team['Full Name']
				value_to_beat = team.FanDuel.sum()
				
				print team.Salary.sum(), team.FanDuel.sum()
				