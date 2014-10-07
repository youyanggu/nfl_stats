"""

Simple data-driven algorithm to predict weekly passing, rushing, and receiving leaders in the NFL.

@author: Youyang Gu

"""

import csv
import operator
import matplotlib.pyplot as plt
import numpy as np

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
STANDINGS_FILE = 'years_2014_standings.csv'
WEEK_PASSING_FILE = 'week_passing.csv'
WEEK_RUSHING_FILE = 'week_rushing.csv'
WEEK_RECEIVING_FILE = 'week_receiving.csv'
			   	

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
			if 'TM' in team_abbr:
				continue # we ignore a player on multiple teams for now
			team = teams[team_abbr]
			team.set_player_stat(col_name, rank, player)

def update_win_loss_record(fname, teams, team_to_abbr):
	def get_index(name):
		return col_name_to_index[name]

	with open(fname, 'rU') as standings_file:
		pass_def_reader = csv.reader(standings_file)
		col_name_to_index = {}
		count = 0
		for row in pass_def_reader:
			if len(row) == 0 or not row[0]:
				continue
			if row[0] == 'Tm':
				for i in range(len(row)):
					col_name_to_index[row[i]] = i
			row[0] = row[0].translate(None, '*+') # Remove trailing * or +
			if row[0] not in team_to_abbr:
				continue
			win_pct = float(row[get_index('W-L%')])
			team = teams[team_to_abbr[row[0]]]
			team.set_win_pct(win_pct)
			count += 1
	if count != 32:
		raise Exception("Missing team")

def get_weekly_stat(fname, teams, team_to_abbr):
	team_dict = {}
	def get_index(name):
		return col_name_to_index[name]

	with open(fname, 'rU') as weekly_file:
		weekly_reader = csv.reader(weekly_file)
		col_name_to_index = {}
		count = 0
		for row in weekly_reader:
			if len(row) == 0 or not row[0]:
				continue
			if row[0] == 'Rk':
				for i in range(len(row)):
					col_name_to_index[row[i]] = i
			try:
				rank = int(row[0])
			except Exception:
				continue
			team = row[get_index('Tm')]
			opp = row[get_index('Opp')]
			player = row[get_index('Player')]
			if team not in teams or opp not in teams:
				continue
			if team not in team_dict:
				team_dict[team] = (rank, team, opp, player)
	return team_dict

def update_teams(teams, team_to_abbr):
	prefix = "week" + str(CUR_WEEK) + "/"
	update_team_stats('pass_def', prefix+PASSING_DEF_FILE, teams, team_to_abbr)
	update_team_stats('rush_def', prefix+RUSHING_DEF_FILE, teams, team_to_abbr)
	update_player_stats('pass_off', prefix+PASSING_OFF_FILE, teams, team_to_abbr)
	update_player_stats('rush_off', prefix+RUSHING_OFF_FILE, teams, team_to_abbr)
	update_player_stats('recv_off', prefix+RECEIVING_OFF_FILE, teams, team_to_abbr)
	update_win_loss_record(prefix+STANDINGS_FILE, teams, team_to_abbr)


def analyze_week(teams, team_to_abbr):
	cur_week_prefix = "week" + str(CUR_WEEK+1) + "/"
	passing_arr, rushing_arr, receiving_arr = [], [], []
	passing = get_weekly_stat(cur_week_prefix+WEEK_PASSING_FILE, teams, team_to_abbr)
	rushing = get_weekly_stat(cur_week_prefix+WEEK_RUSHING_FILE, teams, team_to_abbr)
	receiving = get_weekly_stat(cur_week_prefix+WEEK_RECEIVING_FILE, teams, team_to_abbr)
	for rank, team, opp, player in passing.values():
		# correlation with last week
		passing_arr.append((rank, teams[team].pass_off))
		# correlation with pass def rank
		#passing_arr.append((rank, teams[opp].pass_def))
		# correlation with diff in win %
		#passing_arr.append((rank, teams[team].win_pct - teams[opp].win_pct))
	for rank, team, opp, player in rushing.values():
		rushing_arr.append((rank, teams[team].rush_off))
		#rushing_arr.append((rank, teams[opp].rush_def))
		#rushing_arr.append((rank, teams[team.win_pct - teams[opp].win_pct))
	for rank, team, opp, player in receiving.values():
		receiving_arr.append((rank, teams[team].recv_off))
		#receiving_arr.append((rank, teams[opp].pass_def))
		#receiving_arr.append((rank, teams[team].win_pct - teams[opp].win_pct))
	return passing_arr, rushing_arr, receiving_arr

def plot_graphs(passing, rushing, receiving):
	x,y = zip(*passing)
	fit = np.polyfit(x, y, 1)
	fit_fn = np.poly1d(fit)
	plt.plot(x, y, 'ro', x, fit_fn(x), '--k')
	plt.title('Passing')

	plt.figure()
	x,y = zip(*rushing)
	fit = np.polyfit(x, y, 1)
	fit_fn = np.poly1d(fit)
	plt.plot(x, y, 'ro', x, fit_fn(x), '--k')
	plt.title('Rushing')

	plt.figure()
	x,y = zip(*receiving)
	fit = np.polyfit(x, y, 1)
	fit_fn = np.poly1d(fit)
	plt.plot(x, y, 'ro', x, fit_fn(x), '--k')
	plt.title('Receiving')
	plt.show()

if __name__ == '__main__':
	team_to_abbr, abbr_to_team = generate_abbr_map(TEAM_NAMES_FILE)
	teams = {}
	for abbr in team_to_abbr.values():
		teams[abbr] = Team(abbr, abbr_to_team[abbr])
	next_week = CUR_WEEK + 1
	schedule = get_schedule(next_week, team_to_abbr, SCHEDULE_FILE)
	print "Games @ Week " + str(next_week) + ": " + str(len(schedule))
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
	for matchup in pass_mismatch:
		print str(rank) + ') ' + matchup.print_pass()
		print "   QB: " + matchup.qb()
		rank += 1

	print "=============== RUSHING MISMATCHES ==============="
	rank = 1
	for matchup in rush_mismatch:
		print str(rank) + ') ' + matchup.print_rush()
		print "   RB: " + matchup.rb()
		rank += 1

	print "=============== RECEIVING MISMATCHES ==============="
	rank = 1
	for matchup in recv_mismatch:
		print str(rank) + ') ' + matchup.print_recv()
		print "   WR: " + matchup.wr()
		rank += 1

	#passing_arr, rushing_arr, receiving_arr = analyze_week(teams, team_to_abbr)
	#plot_graphs(passing_arr, rushing_arr, receiving_arr)


