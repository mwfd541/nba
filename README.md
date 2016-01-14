# nba
Python tools that can be used for projections and roster optimization for the NBA

*Disclaimer: In no way do we mean to encourage or condone the corporate practice of profiting by ignoring weakly enforced laws meant to protect citizens.*   

Please note I'm not an experienced developer so I'm just kind of pushing code in whatever way feels right at the time and trying to leave enough notes around so that it might make sense. 


The tools here are used in four steps. 

As of now, in order to use it you need the following files present in the directory:

1) position.csv 

2)gamesprocessed.csv or emptygamesprocessed.csv

3)2014statsD21.csv 

4)opponents.csv

5)team_dict.csv

6)If you're appending, you should have trainsmall.csv 

1)-5) are available in this repository and contain static data.  To apply to an upcoming FD contest, download the contest's csv from FD and save it in the directory as

6) current.csv

### 1 Scraping the latest data and creating a training file - buildtrain.py
This goes to nba.com and downloads player data from every 2015 game up to this date, processes the data, and then saves it into a large training file (train.csv) that can be fed into your favorite machine learning algorithm.   

If this is the first time you run it, the first line of the file should be set to 'app = False', and the file will be build from scratch. This takes a few minutes, so when it is finished it saves the data to a file.  Next time, set 'app = True' and instead of processing all of the data it will only process the recent data.  


### 2 Building a test file for the upcoming contest - buildtest.py
This creates test.csv

### 3 Creating projections for each player in the test file - xgb_fd.py   (recently xgbmulti.py) 
To start, we have xgboost running, which uses the final FanDuel score as a target.  Of course there are many other things one can do to predict this number including using each of the components (ie. AST, FGM, OREB, etc.) as targets and then summing these, or using some other machine learning methods.   

Recently added xgbmulti.py.  This saves each of the predictions in a file named by the date.  All are using xgboost.  One prediction is the straightforward one, another predicts minutes and FDpoints/minute, another predicts each statistic.  The final two use error functions what punish over and under estimations more severely, respectively.    My plan is to go back and compare which predictions (or ensembles) are the most useful and how.   

 xgb_fd.py outputs to nbapred.csv , xgbmult.py outputs to a file named by the date.  

### 4 Generate a roster -    linrand.py or nbaopt.py

These read the data for from nbapredict.csv and the attempts to generate the roster with the highest expected value of points. (This may or not be the best strategy, depending on the contest, but the question of the best strategy is an extremely difficult problem.) 
To get the optimal one, run nbaopt.py.   To generate some other nearby lineups use linrand.py.  The latter uses linear programming, which is relatively fast (as opposed to binary linear programming.)  Linear programming has the disadvantage that the optimizer will often involve fractional players, which won't work for our purposes.  To deal with this we perturb the problem, solve the problem and then extract a (non-fractional) team from this, and test that it still satisfies the constraints.   The output is a sequence of teams with increasing expected value.  Usually, the first few can be ignored, but the latter ones tend to converge towards the optimal team.   
If you are using this to create a roster, be careful to make sure everything smells right:  It does funny things like predicting high scores for rookies who have yet to play in any games or are not even on the roster.  For example, the prediction for Rakeen Christmas seems to be some sort of league average, but because this salary is so low, he almost always ends up on the roster.  So you may have to delete him explicitly either current.csv file.   

## Bugs/Errors
It appears that the gamelog that get scraped doesn't create a record for players that don't enter the game.   So a bunch of zero values are being ignored in the training.  I don't think this is likely to cause a problem, as the guys that far down on the bench are not likely to make it into any lineups.  


## Notes on strategy

Finding the right metric or energy is tricky.   RMSE may nail most of the predictions but if one is well over-estimated and you include that guy in your lineup,  your lineup is ruined.  

My strategy at this point is to use the predictions for FD points per minute * expected minutes, and run an optimizer.  (I'll worry about maximizing the variance soon enough.)  Then what I try to do is read the injury reports and try to modify the expected minutes of the players that will be affected by the injury.   Unfortunately, this is somewhat painstaking and often happens during the workday, so I don't usually get to it.  The real bargains are to be had when the team announces that a player will be out for the upcoming game.  
