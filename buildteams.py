import pandas as pd
from scipy.optimize import linprog
import numpy as np

runs = 1500
Tune_1 = 3
Tune_2	= 2
eta = .5   #it appear from playing around the .5 generates the most teams 

current = pd.read_csv('current.csv')
current = pd.get_dummies(current, columns = ['Position'])
df = pd.read_csv('nbapred.csv')
df = pd.merge(df, current, on = ['Id','Salary','Team'], how = 'left')
df['Full Name']=df['First Name']+' '+df['Last Name']


#This is going to ignore injuries and everything and will assume that everything is considered in the function f.  We can modify this later if we want to mix ensembles up.  

f=-df.FanDuel

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

Sal=list(df.Salary)

A=[Sal,PG,PF,SF,SG,C]
x0_bounds = (0, 1)
teamlist=[]


for p in range(runs):
	ff=f-Tune_1*np.random.randn(len(f))
	B=[60000+Tune_2*1000*np.random.randn(),2,2,2,2,1]

	res = linprog(ff, A_ub=A, b_ub=B, bounds=(x0_bounds),options={"disp": False})
	draft=res.x-eta
	draft = np.ceil(draft)
	
	if draft.dot(Sal)<60001:
			print draft.dot(Sal)
			if (draft.sum()==9):
				print '\n'
				print 'found team'
				print draft
				teamlist = teamlist +[draft]
				print len(teamlist)
teamdf = pd.DataFrame(teamlist)
teamdf.to_csv('teams.csv')
				