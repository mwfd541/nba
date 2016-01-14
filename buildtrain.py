import requests
import pandas as pd
from datetime import datetime

app = False   # If starting from scratch, this should be set to 'False' 
if app: print 'we are appending to an old train file, correct?'
else : print  'we are starting from scratch, correct?'
####  Start by downloading data from nba.com
def load():   ### first thing we do is go get all of the data for the entire year and save it into 2015games.csv
	fout = open('2015games.csv', 'w')
	r = requests.get('http://stats.nba.com/stats/leaguegamelog?Counter=1000000&Direction=DESC&LeagueID=00&PlayerOrTeam=P&Season=2015-16&SeasonType=Regular+Season&Sorter=PTS')
	data = r.json().get('resultSets', [])[0]
	headers = data.get('headers', [])
	rows = data.get('rowSet', [])
	fout.write(','.join(headers))
	fout.write('\n')
	for row in rows:
		fout.write(','.join([str(r) for r in row]))
		fout.write('\n')
				
def games_not_processed(app):   ## returns a dataframe of games which have not been added to the processed list.  Also returns a set of games, which will be added to the processed list once processing is complete.
	try : glist = pd.read_csv('gamesprocessed.csv')
	except : app = False
	if app==False : 
		print 'starting from empty gamesprocessed file'
		glist = pd.read_csv('emptygamesprocessed.csv')
	gl1 = set(glist.GAME_ID)
	wf = pd.read_csv('2015games.csv')
	gl2 = set(wf.GAME_ID)
	gdiff = gl2-gl1
	df = wf[wf['GAME_ID'].isin(gdiff)]   # This selects the subset of unprocessed games
	return df, gdiff
	
	
def home_away(df):  #### this determines home and away for each game and lists the opponent.  Later (but not yet)  we also give the opponent it's own "feature" column.  It takes the dataframe of unprocessed games.   It returns a dataframe 
	df['home']=1
	df['away']=0
	df['Opponent'] = df.MATCHUP
	for z in range(len(df)):
		if len(df.Opponent.iloc[z].split('vs.'))==2:
			df.Opponent.iloc[z]=df.Opponent.iloc[z].split(' vs. ')[1]  #this part is slow for the whole file, for some reason
		else : 
			df.Opponent.iloc[z]=df.Opponent.iloc[z].split(' @ ')[1]
			df.away.iloc[z]=1
			df.home.iloc[z]=0
	return df
	

def position(df):  #### pulls position from a separately created file that remembers the position and adds dummy features to dataframe
	posdf = pd.read_csv('position.csv')
	df = pd.merge(df, posdf, on='PLAYER_NAME', how = 'left')    #just something to be aware of: here we merge on name.  Other places on ID.  This caused me some confusion at one point.   
	df = pd.get_dummies(df, columns = ['Position'])
	return df
	
	


def build_train(recent_df):  #recent_df should be the raw data from nba.com for the games yet processed.  
	stats14 = pd.read_csv('2014statsD21.csv')
	stats14 = stats14.drop('PLAYER_NAME', axis = 1)  # we will be merging on ID instead so don't want two copies 
	recent_df['NewGame']=True
	recent_df['rest']=0
	recent_df['recent_minutes']=-1
	gamelog = recent_df
	gamelog['FanDuel']=2*gamelog['FGM']+gamelog['FG3M']+gamelog['FTM']+1.2*gamelog['REB']+1.5*gamelog['AST']+2*gamelog['BLK']+2*gamelog['STL']-gamelog['TOV']
	df =pd.merge(gamelog, stats14, on='PLAYER_ID', how = 'left')
	
	### I was having some problems with extraneous index columns creeping into the file when I merge.   If there's a different number of these columns, it throws an error when we concatenate.  So the point of the next code is to remove these "unnamed" columns.    Then we will merge with the stored train file.  
	
	u_columns=[]
	for c in df.columns.values:
		if 'Unnamed' in c: 
			u_columns += [c]
	for c in u_columns:
		df = df.drop(c, axis =1)
	if app : 
		dfold=pd.read_csv('trainsmall.csv')
		u_columns=[]
		for c in dfold.columns.values:
			if 'Unnamed' in c: 
				u_columns += [c]
		for c in u_columns:
			dfold = dfold.drop(c, axis =1)
		df=df.append(dfold)
	#df.to_csv('look.csv')
	
	df = df.sort_index(by=['PLAYER_ID','GAME_DATE'], ascending = [True, False])
	
	######################################  Create rest days #############################  This part is slow, not sure how best to speed it up.
	yes = True
	for i in range((len(df))-1):
		if df.NewGame.iloc[i]:
			if df.PLAYER_ID.iloc[i]==df.PLAYER_ID.iloc[i+1]:
				df.recent_minutes.iloc[i]=df.MIN.iloc[i+1] 
				try : d1 = datetime.strptime(df.GAME_DATE.iloc[i+1], "%m/%d/%Y")   
				except : d1 = datetime.strptime(df.GAME_DATE.iloc[i+1], "%Y-%m-%d")
				try: d2 = datetime.strptime(df.GAME_DATE.iloc[i], "%m/%d/%Y")
				except : d2 = datetime.strptime(df.GAME_DATE.iloc[i], "%Y-%m-%d")
				df.rest.iloc[i] = ((d2 - d1).days)
			else : 
				df.rest.iloc[i]=15
	df.NewGame = False
	try:df.to_csv('trainsmall.csv')
	except:
		print "close the file, silly"
		df.to_csv('trainsmallbackup.csv')
		print 'not saving the games processed to list'
		quit()
	df =pd.get_dummies(df, columns = ['Opponent','PLAYER_ID'])
	
	try:df.to_csv('train.csv')
	except:
		print "close the file, silly"
		df.to_csv('trainbackup.csv')
		print 'not saving the games processed to list'
		quit()


load()
df1, b = games_not_processed(app)
print 'processing games' , list(b)
print 'computing home away'
df1 = df1
df = home_away(df1)
print 'adding in position file'
df = position(df)
print 'building train'
build_train(df)
print 'writing games processed to csv'
games = pd.read_csv('gamesprocessed.csv')
gameslist = list(games.GAME_ID)
gameslist = gameslist + list(b)
games = pd.DataFrame(gameslist, columns = ['GAME_ID'])
games.to_csv('gamesprocessed.csv')
quit()

	
		
	
def build_position_file():   ## this was one time shot.   Took several FanDuel files to learn the position data, and then created a file with the position data 
	p1 = pd.read_csv('p1.csv')
	p2 = pd.read_csv('p2.csv')
	p3 = pd.read_csv('p3.csv')

	p = pd.concat([p1,p2,p3])

	p['PLAYER_NAME']=p['First Name']+' '+p['Last Name']
	p = p.sort_index(by = ['PLAYER_NAME'])
	playerlist =[]
	positionlist =[]
	for h in range(len(p)):
		if p.PLAYER_NAME.iloc[h]!=p.PLAYER_NAME.iloc[h-1]:
			playerlist += [p.PLAYER_NAME.iloc[h]]
			positionlist +=[p.Position.iloc[h]]
	

	plist = pd.DataFrame.from_items([('PLAYER_NAME', playerlist),('Position', positionlist)])
	
	plist.to_csv("position.csv")


	
