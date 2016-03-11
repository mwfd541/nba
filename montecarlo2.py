import pandas as pd
import numpy as np

N = 1000 #number of similulate games 
factor = .3   # this tunes the randomness 


teamsdf = pd.read_csv('teams.csv')
teamsdf = teamsdf.drop(teamsdf.columns[0], 1)
TeamMatrix = teamsdf.as_matrix()
current = pd.read_csv('today2.csv')
current.fillna(0,inplace=True)  
f = list(current.FDexpected)
f = np.tile(f, (N,1))
g = list(current.sigma)
g = np.tile(g, (N,1))

players  = len(teamsdf.columns)
teams = len(teamsdf.index)
RandomMatrix = np.random.randn(players,N)
NotRandomMatrix = np.ones((players,N))
PlayerScores = RandomMatrix*g.transpose()+NotRandomMatrix*f.transpose()
TeamScores = TeamMatrix.dot(PlayerScores)

TeamRanks = np.empty((teams, N))
for i in range(N):
	x = TeamScores[:,i]
	seq = sorted(x)
	index = [seq.index(v) for v in x]
	TeamRanks[:,i] = index

Quintile = TeamRanks - 0.8*teams
Quintile = np.sign(Quintile)+1
Quintilewins = Quintile.dot(np.ones(N)) /2


Tertiale = TeamRanks - 0.67*teams
Tertiale = np.sign(Tertiale)+1
Tertialewins = Tertiale.dot(np.ones(N)) /2


Fifty = TeamRanks - 0.5*teams
Fifty = np.sign(Fifty)+1
Fiftywins = Fifty.dot(np.ones(N)) /2
data = [Quintilewins, Tertialewins, Fiftywins]

Qdf = pd.DataFrame(data, index = ['Quintile','Top Third','50/50'])
Qdf.to_csv('qdf.csv')

topteams =[]  		## This little piece is to create three lists of the top teams.   I'm calling it top10, but what is actually happening is that the list is first sorted, and then for the top 5 scores, all the teams achieving the top 5 scores are saved.   ### This comment no longer relevant.  I'm just taking the best team in each group now.  
for x in data:
	seq = sorted(x)
	top10 =[]
	for v in seq[-1:]:
		xloc = np.where(x == v)[0]
		top10 = top10 + list(xloc)
	topteams = topteams +[top10]
	for j in top10 : print x[j]
	print '\n'

print topteams

current = pd.read_csv('current.csv')
label = 20 

def display_a_team_from_a_team_vector(x):	
	x = np.array(x)
	B = x.astype(bool)
	Team = current[B][['Position','First Name', 'Last Name','Salary']]
	print Team

z = 0
disp=['Quint', 'Tert', 'Half']
for l in topteams:
	for m in l:
		print 'Team in group', disp[z]
		display_a_team_from_a_team_vector(list(teamsdf.iloc[m]))
	z =z+1
quit()


