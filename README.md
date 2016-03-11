# nba
Python tools that can be used for projections and roster optimization for the NBA

Please note I'm not still learning as developer - so I welcome any comments or criticisms. 

The idea is the following:  Scrape nba stats website for up to date data, then run xgboost, testing the FanDuel players for the upcoming contest.  A prediction for each player is made in terms of expected minutes, and and expected FDpoints/minute, and this is multiplied together to get an expected value.   Using this expected value, we build a few hundred teams by adding some noise to the expected value, and then running a linear optimization programs to select an optimal team.  Then, we compute the standard deviation of each player.   Finally, we use a monte carlo method which gives assigns to each player a random value based on his expected value and standard deviation.  The totals for all the teams are compared, and ranked.   Then the processed is repeated a few thousand times, and the teams which show up in this top quintile, third, and half are displayed.  

For some odd reason, about a month stats.nba.com stopped responding to the python requests, unless I went there with my browser.  So the quick fix to this is to simply enter the url in your browser, then run buildtrain.py

Note that the major wrinkle in this game is injuries and rested players.  This throws everything off, even if it's not your player,  because everyone else appears to be optimizing.  If a player is benched in the hours leading up to the game, his replacements value goes up quite a bit, which puts this player in many lineups.   Figuring out how this works is not so easy.  As of now, if I see that a player has been benched, I modify the file today.csv (following step 3 below) and increase minutes of the players I think will be absorbing these minutes.  Presumably the points/minute won't change that much, so this gives me a good estimate on how the backup player is worth.  I'm in the process of using a covariance matrix to adjust this automatically.  I'm also snooping around to see if there is good substitution data available - the idea being that a substitution matrix could be iterated as a Markov chain to predict how the players minutes are diffused to his teammates.  

There's some processing of the data that takes a bit, but I store this in a file, and also store the games I have processed. This way, while we download the entire stats for 2015-16 every day, we only process the most recent games.  This saves a ton of time.  

There's five python scripts that need to be run in order

1) buildtrain.py
2) buildtest.py
3) xgbx.py
4) buildteams2.py
5) montecarlo2.py


As of now, in order to use it you need the following files present in the directory:

1) position.csv 

2)gamesprocessed.csv or emptygamesprocessed.csv

3)2014statsD21.csv 

4)opponents.csv

5)team_dict.csv

6)If you're appending, you should have trainsmall.csv 

7) df6.csv  (this includes salary data and some backtested values that seemed to improve the performance of xgboost) 

1)-5) are available in this repository and contain static data.  To apply to an upcoming FD contest, download the contest's csv from FD and save it in the directory as

8) current.csv

### 1 Scraping the latest data and creating a training file - buildtrain.py
This goes to nba.com and downloads player data from every 2015 game up to this date, processes the data, and then saves it into a large training file (train.csv) that can be fed into your favorite machine learning algorithm.   

If this is the first time you run it, the first line of the file should be set to 'app = False', and the file will be build from scratch. This takes a few minutes, so when it is finished it saves the data to a file.  Next time, set 'app = True' and instead of processing all of the data it will only process the recent data.  


### 2 Building a test file for the upcoming contest - buildtest.py
This creates test.csv, then test2.csv, train2.csv with some extra features I added later. 

### 3 Creating projections for each player in the test file - xgbx.py   (recently xgbmulti.py) 
this run the Extreme Gradient Boost - you should have xgboost installed.  It outputs to a file today.csv.     
te.  

### 4 Generate a roster -    linrand.py or nbaopt.py.   Recently added buildteams and montecarlo

These read the data for from nbapredict.csv and the attempts to generate the roster with the highest expected value of points. (This may or not be the best strategy, depending on the contest, but the question of the best strategy is an extremely difficult problem.) 
To get the optimal one, run nbaopt.py.   To generate some other nearby lineups use linrand.py.  The latter uses linear programming, which is relatively fast (as opposed to binary linear programming.)  Linear programming has the disadvantage that the optimizer will often involve fractional players, which won't work for our purposes.  To deal with this we perturb the problem, solve the problem and then extract a (non-fractional) team from this, and test that it still satisfies the constraints.   The output is a sequence of teams with increasing expected value.  Usually, the first few can be ignored, but the latter ones tend to converge towards the optimal team.   
If you are using this to create a roster, be careful to make sure everything smells right:  It does funny things like predicting high scores for rookies who have yet to play in any games or are not even on the roster.  For example, the prediction for Rakeen Christmas seems to be some sort of league average, but because this salary is so low, he almost always ends up on the roster.  So you may have to delete him explicitly either current.csv file.   

The buildteams.py will generate a collection of teams in the same linear programming way as linrand. There are some parameters that can be tuned if the teams are too concentrated or too random.   After generating a number of these, montecarlo runs a number of simulations, and ranks the teams for each simulations and then gives back the teams which show up most frequently in the top fifth, third and half.  After observing that the median of a contest varies quite a bit day-to-day, despite the expected mean or median staying close - it seems that what one should do, instead of "maximize variance" one should try to "maximize relative variance" under the realization that many of the competiting rosters will be somewhat similar. This is an attempt to follow this strategy. 

## Bugs/Errors
It appears that the gamelog that get scraped doesn't create a record for players that don't enter the game.   So a bunch of zero values are being ignored in the training.  I don't think this is likely to cause a problem, as the guys that far down on the bench are not likely to make it into any lineups.  


## Notes on strategy

Finding the right metric or energy is tricky.   RMSE may nail most of the predictions but if one is well over-estimated and you include that guy in your lineup,  your lineup is ruined.  

My strategy at this point is to use the predictions for FD points per minute * expected minutes, and run a monte carlo.  The hope is that the naturally occuring correlations between players are dealt with in the monte carlo. 
