"""

Simple data-driven algorithm to predict weekly passing, rushing, and receiving leaders in the NFL.

@author: Youyang Gu

"""

import csv
import operator
from team import Team
from matchup import Matchup

CUR_WEEK = 5
TEAM_NAMES_FILE = 'team_names.csv'
SCHEDULE_FILE = 'years_2014_games_games_left.csv'
PASSING_DEF_FILE = 'years_2014_opp_passing.csv'
RUSHING_DEF_FILE = 'years_2014_opp_rushing.csv'
PASSING_OFF_FILE = 'years_2014_passing_passing.csv'
RUSHING_OFF_FILE = 'years_2014_rushing_rushing_and_receiving.csv'
RECEIVING_OFF_FILE = 'years_2014_receiving_receiving.csv'

def get_win_pct(record):
	if '/' in record:
		w, l, t = [int(i) for i in record.split('/')]
	elif '-' in record:
		w, l, t = [int(i) for i in record.split('-')]
	else:
		return 0
	games = w + l + t
	return round(w * 1.0 / games, 2)
			   	

def generate_abbr_map(fname):
	team_to_abbr = {}
	abbr_to_team = {}
	with open(fname, 'rU') as team_names_file:
		team_names_reader = csv.reader(team_names_file)
		for team_name, team_abbr in team_names_reader:
			team_to_abbr[team_name] = team_abbr
			abbr_to_team[team_abbr] = team_name
	return team_to_abbr, abbr_to_team

def get_schedule(week, team_to_abbr, fname):
	games = []
	with open(fname, 'rU') as schedule_file:
		schedule_reader = csv.reader(schedule_file)
		for row in schedule_reader:
			if len(row) != 8:
				continue
			try:
				cur_week = int(row[0])
			except Exception:
				continue
			if cur_week < week:
				continue
			if cur_week > week:
				break
			visit_team = row[3]
			home_team = row[5]
			if visit_team not in team_to_abbr or home_team not in team_to_abbr:
				raise Exception("Team not in dictionary")
			games.append((team_to_abbr[visit_team], team_to_abbr[home_team]))
	return games

def update_team_stats(col_name, fname, teams, team_to_abbr):
	def get_index(name):
		return col_name_to_index[name]

	with open(fname, 'rU') as pass_def_file:
		pass_def_reader = csv.reader(pass_def_file)
		col_name_to_index = {}
		for row in pass_def_reader:
			if len(row) == 0:
				continue
			if row[0] == 'Rk':
				for i in range(len(row)):
					col_name_to_index[row[i]] = i
			try:
				rank = int(row[0])
			except Exception:
				continue
			team_abbr = team_to_abbr[row[get_index('Tm')]]
			team = teams[team_abbr]
			team.set_team_stat(col_name, rank)

def update_player_stats(col_name, fname, teams, team_to_abbr):
	def get_index(name):
		return col_name_to_index[name]

	with open(fname, 'rU') as pass_def_file:
		pass_def_reader = csv.reader(pass_def_file)
		col_name_to_index = {}
		for row in pass_def_reader:
			if len(row) == 0:
				continue
			if row[0] == 'Rk':
				for i in range(len(row)):
					col_name_to_index[row[i]] = i
			try:
				rank = int(row[0])
			except Exception:
				continue
			player = row[get_index('Player')]
			team_abbr = row[get_index('Tm')]
			team = teams[team_abbr]
			team.set_player_stat(col_name, rank, player)
			if col_name == 'pass_off':
				record = row[get_index('QBrec')]
				win_pct = get_win_pct(record)
				team.set_win_pct(win_pct)

def update_teams(teams, team_to_abbr):
	update_team_stats('pass_def', PASSING_DEF_FILE, teams, team_to_abbr)
	update_team_stats('rush_def', RUSHING_DEF_FILE, teams, team_to_abbr)
	update_player_stats('pass_off', PASSING_OFF_FILE, teams, team_to_abbr)
	update_player_stats('rush_off', RUSHING_OFF_FILE, teams, team_to_abbr)
	update_player_stats('recv_off', RECEIVING_OFF_FILE, teams, team_to_abbr)


if __name__ == '__main__':
	team_to_abbr, abbr_to_team = generate_abbr_map(TEAM_NAMES_FILE)
	teams = {}
	for abbr in team_to_abbr.values():
		teams[abbr] = Team(abbr, abbr_to_team[abbr])
	schedule = get_schedule(CUR_WEEK, team_to_abbr, SCHEDULE_FILE)
	print "Games @ Week " + str(CUR_WEEK) + ": " + str(len(schedule))
	update_teams(teams, team_to_abbr)

	for team in teams.values():
		print team

	matchups = []
	for visit_team, home_team in schedule:
		visit = teams[visit_team]
		home = teams[home_team]
		matchups.append(Matchup(visit, home, False, CUR_WEEK))
		matchups.append(Matchup(home, visit, True, CUR_WEEK))

	pass_mismatch = sorted(matchups, key=operator.attrgetter('pass_score'), reverse=True)
	rush_mismatch = sorted(matchups, key=operator.attrgetter('rush_score'), reverse=True)
	recv_mismatch = sorted(matchups, key=operator.attrgetter('recv_score'), reverse=True)

	print "=============== PASSING MISMATCHES ==============="
	rank = 1
	for matchup in pass_mismatch[:10]:
		print str(rank) + ') ' + matchup.print_pass()
		print "   QB: " + matchup.qb()
		rank += 1

	print "=============== RUSHING MISMATCHES ==============="
	rank = 1
	for matchup in rush_mismatch[:10]:
		print str(rank) + ') ' + matchup.print_rush()
		print "   RB: " + matchup.rb()
		rank += 1

	print "=============== RECEIVING MISMATCHES ==============="
	rank = 1
	for matchup in recv_mismatch[:10]:
		print str(rank) + ') ' + matchup.print_recv()
		print "   WR: " + matchup.wr()
		rank += 1

