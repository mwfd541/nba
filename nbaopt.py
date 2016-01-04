#  This takes the csv file from fanduel, with a column "points" used at the predictor 
# this removes anyone who is injured.   
#need to fix the injury indicator colum
##  Need to add some handling of the case that the optimal value is spending 0 on a position - perhaps just fill the 0  with lowest value ?  
import pandas as pd
import numpy as np
#import pickle


#read the file


current = pd.read_csv('current.csv')
df = pd.read_csv('nbapred.csv')
df = pd.merge(df, current, on = ['Id','Salary','Team'], how = 'left')
df['Full Name']=df['First Name']+' '+df['Last Name']


df['Salary']=df['Salary']/100


df['InjuryIndicator']=df['Injury Indicator'].fillna(0)
for z in df.index:
	if df.InjuryIndicator[z] !=0 :
		print "injured:", df['First Name'][z],df['Last Name'][z]
		df = df.drop(z)

#split into dataframes for each position

PG=df[df['Position'] == 'PG']
SG=df[df['Position'] == 'SG']
SF=df[df['Position'] == 'SF']
PF=df[df['Position'] == 'PF']
C=df[df['Position'] == 'C']

#The following function takes a position (i.e a dataframe )
	
def reduce_two(dfin):
	df=dfin.sort(['Salary'])
	m1=0
	m2=0
	for x in df.index:
		if df.FanDuel[x]>m1:
			m1=df.FanDuel[x]
			continue
		if df.FanDuel[x]>m2:
			m2=df.FanDuel[x]
			continue
		df=df.drop(x)
	return df

	
	
def reduce_one(dfin):
	df=dfin.sort(['Salary'])
	m1=0
	for x in df.index:
		if df.FanDuel[x]>m1:
			m1=df.FanDuel[x]
			continue
		df=df.drop(x)
	return df
	
SF=reduce_two(SF)
PG=reduce_two(PG)
PF=reduce_two(PF)
SG=reduce_two(SG)
C=reduce_one(C)   





def best_two(dfin):  #this takes a dataframe with Salary and FPPG and returns a list from 0 to 600 indicating how much FPPG can be purchased for that ammount.      I'm sure there's some clever way to optimize this so I don't test as many cases. 
	value_list=np.zeros(601)
	id_list1 = [0]*601
	id_list2 = [0]*601
	bestotherrem=0
	bestchoicerem=0
	for i in range(601):
		V = 0
		for y in dfin.index:
			yother = dfin.drop(y)
			yother = yother[yother['Salary'] + dfin.Salary[y]<=i]
			try : 
				bestother = yother.FanDuel.idxmax()
				bestvalue =  yother.FanDuel[bestother]+dfin.FanDuel[y]
			except : 
				bestother = 0
				bestvalue = 0
				bestchoice = 0
			if bestvalue>V : 
				V=bestvalue
				bestchoice = y
				bestotherrem=bestother
				bestchoicerem=bestchoice
		value_list[i]=V	
		id_list1[i]=bestchoicerem
		id_list2[i]=bestotherrem
	return value_list, id_list1, id_list2


def best_one(dfin):  #this will return the whole list   
	value_list=np.zeros(601)
	id_list  = [0]*601
	for i in range(601):
		V = 0
		df2 = dfin[dfin['Salary']<=i]
		try : 
			bestother = df2.FanDuel.idxmax()
			bestvalue =  df2.FanDuel[bestother]
		except : 
			bestother = 0
			bestvalue = 0
		if bestvalue>V :
				V=bestvalue
				bestcenter = bestother
		value_list[i]=V	
		id_list[i]=bestother
	return value_list, id_list

PFV, PF1, PF2 = best_two(PF)
print 'pfv done'
PFdf = pd.DataFrame({'a': PFV, 'b': PF1, 'c':PF2})
#print df.head(250)
SFV,SF1,SF2 = best_two(SF)
print 'sfv done'
PGV,PG1,PG2 = best_two(PG)
print 'pgv done'
SGV,SG1,SG2 = best_two(SG)
print 'sgv done'
"""
pickle.dump(PGV, open( "PG.p", "wb" ) )

pickle.dump(SGV, open( "SG.p", "wb" ) )

pickle.dump(SFV, open( "SF.p", "wb" ) )

pickle.dump(PFV, open( "PF.p", "wb" ) )"""


CV, C1 = best_one(C)
print 'c done'

"""
PGV = pickle.load( open( "PG.p", "rb" ) )

SFV = pickle.load( open( "SF.p", "rb" ) )


PFV = pickle.load( open( "PF.p", "rb" ) )

SGV = pickle.load( open( "SG.p", "rb" ) )"""
# now combine the guards
GG = np.zeros(601)
PGinGG=[0]*601

SGinGG=[0]*601

for i in range(601):

	A = PGV[:i+1]
	B = SGV[:i+1]
	Anull = [x !=0 for x in A]   #we're setting up a test to only allow values where both positions are used 
	An=[int(x) for x in Anull]
	
	Bnull = [x !=0 for x in B]   #we're setting up a test to only allow values where both positions are used 
	Bn=[int(x) for x in Anull]
	
	AB=A+B[::-1]
	AB=np.multiply(AB,An)
	AB=np.multiply(AB,Bn)
	try: 
		Amax = np.argmax(AB)
		ABmax = np.amax(AB)
	except:
		Amax = 0
		ABmax = 0
	Bmax = i-Amax
	GG[i]=ABmax
	SGinGG[i]=Bmax
	PGinGG[i]=Amax
	 

# now combine the forwards

FF = np.zeros(601)
PFinFF=[0]*601

SFinFF=[0]*601

for i in range(601):
	A = PFV[:i+1]
	B = SFV[:i+1]
	Anull = [x !=0 for x in A]   #we're setting up a test to only allow values where both positions are used 
	An=[int(x) for x in Anull]
	
	Bnull = [x !=0 for x in B]   #we're setting up a test to only allow values where both positions are used 
	Bn=[int(x) for x in Anull]
	
	AB=A+B[::-1]
	AB=np.multiply(AB,An)
	AB=np.multiply(AB,Bn)
	try: 
		Amax = np.argmax(AB)
		ABmax = np.amax(AB)
	except:
		Amax = 0
		ABmax = 0
	Bmax = i-Amax
	FF[i]=ABmax
	SFinFF[i]=Bmax
	PFinFF[i]=Amax

	
#now combine forwards and gaurds

FFGG = np.zeros(601)
FFinFG=[0]*601
GGinFG=[0]*601

for i in range(601):
	A = GG[:i+1]
	B = FF[:i+1]
	Anull = [x !=0 for x in A]   #we're setting up a test to only allow values where both positions are used 
	An=[int(x) for x in Anull]
	
	Bnull = [x !=0 for x in B]   #we're setting up a test to only allow values where both positions are used 
	Bn=[int(x) for x in Anull]
	
	AB=A+B[::-1]
	AB=np.multiply(AB,An)
	AB=np.multiply(AB,Bn)    #this is a bug - the reversed order isn't here!!!!
	try: 
		Amax = np.argmax(AB)
		ABmax = np.amax(AB)
	except:
		Amax = 0
		ABmax = 0
	Bmax = i-Amax   #something here - need to check this is what it is supposed to be
	FFGG[i]=ABmax
	GGinFG[i]=Amax
	FFinFG[i]=Bmax



#finally combine all with the centers


A = FFGG
B = CV
Anull = [x !=0 for x in A]   #we're setting up a test to only allow values where both positions are used 
An=[int(x) for x in Anull]
	
Bnull = [x !=0 for x in B]   #we're setting up a test to only allow values where both positions are used 
Bn=[int(x) for x in Anull]
	
AB=A+B[::-1]
AB=np.multiply(AB,An)
AB=np.multiply(AB,Bn)
try: 
	Amax = np.argmax(AB)
	ABmax = np.amax(AB)
except:
	Amax = 0
	ABmax = 0
Bmax = i-Amax
print "maximum is ", ABmax
print "spend ", Bmax, "on centers"
print "spend", Amax, "on the rest"
Cspend = Bmax
Gspend =  GGinFG[Amax]
Fspend =  FFinFG[Amax]
print "in particular, spending ", Amax, "on FFGG should give you", FFGG[Amax]
print "this last bit splits into  GG:", Gspend, GG[Gspend], "FF:", FFinFG[Amax], FF[Fspend]

print "spend ", PGinGG[Gspend], "on PG and ", SGinGG[Gspend], "on SG"

print "spend ", PFinFF[Fspend], "on PF and ", SFinFF[Fspend], "on SF"

pf1 = PF1[PFinFF[Fspend]]
pf2 = PF2[PFinFF[Fspend]]

sf1 = SF1[SFinFF[Fspend]]
sf2 = SF2[SFinFF[Fspend]]


pg1 = PG1[PGinGG[Gspend]]
pg2 = PG2[PGinGG[Gspend]]


sg1 = SG1[SGinGG[Gspend]]
sg2 = SG2[SGinGG[Gspend]]

center = C1[Cspend]


team = [pf1, pf2, sf1, sf2, pg1, pg2, sg1, sg2, center]
for j in team:
	print df['Full Name'][j],df['FPPG'][j], df['FanDuel'][j],df['Salary'][j]


	
	
	