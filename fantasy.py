import pandas as pd
import requests


'''IDP TD - TD, TD.1 - +6
Sack - SK - +4
Sack Yards - .2 points per yard *** - https://www.teamrankings.com/nfl/player-stat/defense-sack-yards
Hit on QB - QBHits - +1
Tackle for loss - TFL - +2
Blocked Punt, PAT or FG + +3 ***
INT - Int - +4
INT return yards - Yds - +.2 points per yard
Fumble recovery - FR - +3
Fumble Return yards - Yds.1 - 0.2 * yards
Forced fumble - FF - +3 
Safety - - Sfty - +3
Assisted Tackle - Ast - +1
Solo Tackle - Solo - +2
Pass defended -Pd -  +2
'''

'''
roster ID to team
1 - TP4bunghole
2 - jwestgbr
3 - ob32
4 - lnolley
5 - peenballs
6 - mtringi
7 - SpaceMonkeyBallz4god
8 - jrosenbohm
9 - speedPubert
10 - mxwilk
11 - Reids Butt Hurts
12 - jbartolome
'''


'''
to get position breakdown:
in python environment
from fantasy import *
point_breakdown("7"):
'''
league_id = "992520246835605504"
teams =12
offense = ['WR', 'G', 'TE', 'OT', 'RB', 'T', 'QB', 'OL', 'FB', 'C','OG']
defense = ['S',  'LB', 'DE', 'FS', 'CB', 'SS', 'DB',  'NT', 'ILB',  'OLB', 'DT','DL']
special = ['K','P','LS' ]
team_defense =['DEF']

fan_positions = {'OL', 'TE', 'DB', 'DEF', 'RB', 'QB', 'OG', 'WR', 'LB', 'OT', 'P', 'DL', 'K', 'LEO', 'LS'}
fan_offense = ['OL','TE','RB','QB','OG','WR','OT','LS']
fan_defense = ['DB','DEF', 'LB','DL','LEO']
fan_special = ['K','P']

#GET https://api.sleeper.app/v1/league/992520246835605504/matchups/5


def load_players():
	#returns dataframe with all players in it
	players = pd.read_json("players_sleeper")
	players_transposed = players.transpose()
	return players_transposed


def load_week(week):
	#loads players from downloaded json or downloads matchup
	try:
		df = pd.read_csv("wk" + week + "_sleeper")
	except:
		get_weekly_matchups(week)
		df = pd.read_csv("wk" + week + "_sleeper")
	return df



def get_weekly_matchups(week, players):
	#inputs: week as string
	weekly_data = requests.get("https://api.sleeper.app/v1/league/"+ league_id + "/matchups/" + week)
	if weekly_data.status_code == 200:
		df = pd.read_json(weekly_data.text)
		df[["offense_points","defense_points","special_teams_points"]] = 0
		df["week"] = week
		for i in range(len(df)):
			df.loc[i,"offense_points"], df.loc[i,"defense_points"], df.loc[i,"special_teams_points"] = week_point_breakdown(df.loc[i,"starters_points"], df.loc[i,"starters"], players)
		df.to_csv("wk" + week + "_sleeper")

	else:
		print("there was an error downloading the data.")
		print("status code:" + weekly_data.status_code)
		print("return text"+ weekly_data.text)

'''
for i in fan_pos:
	try:
		for j in i:
			all_pos.append(j)
	except:
		pass
'''
def player_type(player_id, players):
	#player id as string, 
	#returns 0 or offense, 1 for defense, 2 for special teams, 3 for error 
	#players = load_players()
	pos = players.loc[player_id].fantasy_positions[0]
	if pos in fan_offense:
		return 0
	elif pos in fan_defense:
		return 1
	elif pos in fan_special:
		return 2
	else: 
		print(players.loc[player_id].fantasy_positions)
		return 3

def download_all_weeks():
	players = load_players()
	for i in range(1,19):
		get_weekly_matchups(str(i), players)

def week_point_breakdown(starters_points, starters, players):
	t_offense,t_defense, t_special = 0,0,0
	for i in range(len(starters)):
		position = player_type(starters[i], players)
		if position == 0:
			t_offense = t_offense + float(starters_points[i])
		elif position ==1:
			t_defense = t_defense + float(starters_points[i])
		elif position == 2:
			t_special = t_special + float(starters_points[i])
		else:
			return "error"
	return t_offense, t_defense, t_special

'''
from fantasy import *
df = load_week("7")
starters = df['starters'][0]
starters_points = df['starters_points'][0]
week_point_breakdown(starters_points, starters)
'''
'''
lo
for i in range(teams):
'''

#players.loc[str(df[["starters_points","starters"]].iloc[0]['starters'][0])].fantasy_positions[0]
def combine_scores(curr_week):
	frames=[]
	for i in range(1,int(curr_week)+1):
		frames.append(pd.read_csv("wk" + str(i)+ "_sleeper"))
	all_scores = pd.concat(frames)
	return all_scores


def point_breakdown(curr_week):
	all_scores = combine_scores(curr_week)

	points = all_scores.groupby("roster_id")[["offense_points","defense_points","special_teams_points","points"]].sum()

	points = name_rosters(points)
	points["defense_per"] = points["defense_points"]*100 / (points["defense_points"]+ points["offense_points"] + points["special_teams_points"])
	points["offense_per"] = points["defense_points"]*100 / (points["defense_points"] + points["offense_points"] + points["special_teams_points"])
	points["special_per"] = points["special_teams_points"]*100 / (points["defense_points"] + points["offense_points"] + points["special_teams_points"])
	return points

def name_rosters(df):
	df["name"] = ""
	df.loc[1,"name"] = "TP4bunghole"
	df.loc[2,"name"] =  "jwestgbr"
	df.loc[3,"name"] =  "ob32"
	df.loc[4,"name"] =  "lnolley"
	df.loc[5,"name"] =  "peenballs"
	df.loc[6,"name"] =  "mtringi"
	df.loc[7,"name"] =  "SpaceMonkeyBallz4god"
	df.loc[8,"name"] =  "jrosenbohm"
	df.loc[9,"name"] =  "speedPubert"
	df.loc[10,"name"] =  "mxwilk"
	df.loc[11,"name"] =  "Reids Butt Hurts"
	df.loc[12,"name"] =  "jbartolome"
	return df



'''
Doesnt work yet:
def points_breakdown_pos(position):
	pos_points = position + "_points"
	all_scores = combine_scores(18)
	all_scores[pos_points] = 0
	players = load_players()

	for i in range(len(all_scores)): 
		starters = all_scores.loc[i,"starters"]
		starters_points = all_scores.loc[i,"starters_points"]
		for j in range(len(starters)):
			player_id = starters[j]
			pos = players.loc[player_id].fantasy_positions[0]
			if pos == position:
				all_scores.loc[i,pos_points] = all_scores.loc[i,pos_points] + scores[j]
	points = all_scores.groupby("roster_id")[[pos_points, "points"]].sum()
	points = name_rosters(points)
	points[pos_points + "_per"] = points[pos_points] *100 / points["points"]
	return points
'''

'''
pos = players.loc[player_id].fantasy_positions[0]
df.loc[i,"offense_points"], df.loc[i,"defense_points"], df.loc[i,"special_teams_points"] = week_point_breakdown(df.loc[i,"starters_points"], df.loc[i,"starters"])
'''


