
import pandas as pd
import datetime


TODAY = datetime.datetime.today()
tomorrow = TODAY + datetime.timedelta(days=1)
CONTEST_DATE = tomorrow.strftime("%m/%d/%Y")
print "today's date is ",  TODAY.strftime("%m/%d/%Y"), "assuming this is for tomorrow's contest" , CONTEST_DATE

#CONTEST_DATE = '12/25/2015'    If the game is not tomorrw, just put the game date put in by hand here.  Used to compute the days of rest in the test file

				


	
def most_recent_game():##############  This computes the date of the last game for every player, and saves it to a file.   This does not depend on any previous processing (and it quick enough) so that it completes the whole thing.  Assumes that we have 
	gamelog = pd.read_csv('2015games.csv')
	lastgame = gamelog.groupby(['PLAYER_NAME'])['GAME_DATE'].max()
	lastgame = pd.Series.to_frame(lastgame)
	lastgame.to_csv('lastgame.csv')
	
	
def build_test():
	today = pd.read_csv('current.csv')
	for i in today.index:  #### so far these are the discrepencies in the names I've found.  I'm turning the names in FanDuel into names of the NBA stats
		if today['First Name'][i]=='Brad': 
			today['First Name'][i]='Bradley'
			continue
		
		if today['First Name'][i]=='C.J.': 
			today['First Name'][i]='CJ'
			continue
		
		if today['First Name'][i]=='T.J.': 
			today['First Name'][i]='TJ'
		
		
		if today['First Name'][i]=='K.J.': 
			today['First Name'][i]='KJ'
		
		if today['First Name'][i]=='P.J.': 
			today['First Name'][i]='PJ'
		
		if today['First Name'][i]=='J.J.': 
			today['First Name'][i]='JJ'
		
		if today['First Name'][i]=='Ishmael': 
			today['First Name'][i]='Ish'
		
		if today['First Name'][i]=='Jakarr': 
			today['First Name'][i]='JaKarr'
		
		if today['Last Name'][i]=='Hilario': 
			today['Last Name'][i]=''
		
		if today['First Name'][i]=='Chuck': 
			today['First Name'][i]='Charles'
		
		
	teamfile = pd.read_csv('team_dict.csv')    #some abbreviations in FanDuel are different than on NBA stats 
	lastyearfile = pd.read_csv('2014statsD21.csv')
	lastgamefile = pd.read_csv('lastgame.csv')
	#### home away
	today['home']=0
	today['away']=1
	for z in today.index:
		if today.Game[z].split('@')[1]==today.Team[z]:
			today.home[z] = 1
			today.away[z]=0
	today.rename(columns={'Opponent': 'OpponentFD'}, inplace=True)
	today = pd.merge(today,teamfile,on = 'OpponentFD',how = 'left')
	
	today['PLAYER_NAME']=today['First Name']+' '+today['Last Name']
	for i in today.index:
		if today.PLAYER_NAME[i]=='Nene ': today.PLAYER_NAME[i]='Nene'
		if today.PLAYER_NAME[i]=='Louis Amundson': today.PLAYER_NAME[i]='Lou Amundson'
		if today.PLAYER_NAME[i]=='Luc Richard Mbah a Moute': today.PLAYER_NAME[i]='Luc Mbah a Moute'
		if today.PLAYER_NAME[i]=='Roy Devyn Marble': today.PLAYER_NAME[i]='Devyn Marble'
		if today.PLAYER_NAME[i]=='Glenn Robinson III': today.PLAYER_NAME[i]='Glenn Robinson'
		
		if today.PLAYER_NAME[i]=='Phil (Flip) Pressey': today.PLAYER_NAME[i]='Phil Pressey'

	########## compute rest days
	today =pd.merge(today, lastgamefile, on ='PLAYER_NAME', how = 'left')
	restlist = today.GAME_DATE
	restdays = [0]*len(restlist)
	gamedate = datetime.datetime.strptime(CONTEST_DATE, "%m/%d/%Y")
	for k in range(len(restlist)):
		try : d1 = datetime.datetime.strptime(restlist[k], "%m/%d/%Y")   
		except :
			try : d1 = datetime.datetime.strptime(restlist[k], "%Y-%m-%d")
			except : 
				restdays[k]=-1   #hey, we tried.   Can't figure out why fillna isn't working for me 
				continue
		restdays[k]=((gamedate-d1).days)
	today['rest']=restdays
	 
	######## compute recent minues
	gamelog = pd.read_csv('2015games.csv')
	gamelog = gamelog[['PLAYER_NAME','GAME_DATE','MIN', 'PLAYER_ID']]
	gamelog.rename(columns={'MIN': 'recent_minutes'}, inplace=True)
	today = pd.merge(today, gamelog, on =['PLAYER_NAME','GAME_DATE'], how='left')  #- because the only game date in file is the last game, this gives last minutes.  
	
	lastyearfile.rename(columns={'PLAYER_ID': 'PLAYERIDB'}, inplace=True)  #Sort of an odd solution: I wanted to make sure I get correct player ID when I merge so left this in during testing. I went to drop it and it didn't work exactly as I expected (perhaps it's behaving like an index? ) so I leave it as it is, it's harmless.    
	
	test = pd.merge(today, lastyearfile, on ='PLAYER_NAME', how = 'left')
	test.PLAYER_ID = test.PLAYER_ID.fillna(0)   #some players who haven't played this year don't seem to have player ID showing up correctly.  So far these are all injured, so I'm putting it to zero and then deleting the dummy column. 
	
	test[['PLAYER_ID']] = test[['PLAYER_ID']].astype(int) 	#I'm not sure how the player id was converted to a float.  In any case, this fixes it.  

	test.to_csv('testsmall.csv')
	
	test[['PLAYER_ID_COPY']] = test[['PLAYER_ID']]   #not sure how to use get_dummies without getting rid of the column.  The player ID is nice to have handy in the test file. 
	test =pd.get_dummies(test, columns = ['Opponent','PLAYER_ID','Position'])
	test.rename(columns={'PLAYER_ID_COPY': 'PLAYER_ID'}, inplace=True)
	test.to_csv('test.csv')
	


print "tomorrow's date is ", CONTEST_DATE
print 'computing most recent...'
most_recent_game()
build_test()
quit()

