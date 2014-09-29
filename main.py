"""

Simple data-driven algorithm to predict weekly passing, rushing, and receiving leaders in the NFL.

@author: Youyang Gu

"""

import csv
import operator

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


def calc_score(off_rank, def_rank, home, win_pct_diff):
	score = round((off_rank - def_rank) * 1.0 / (off_rank + 5), 2)
	# Home field advantage
	if not home:
		score += abs(score)*0.25
	# Better team advantage
	score -= win_pct_diff*(CUR_WEEK / 2.0)
	return score


class Team:
	def __init__(self, team_abbr, team_name):
		self.team_abbr = team_abbr
		self.team_name = team_name

		self.pass_def = None
		self.rush_def = None
		self.pass_off = None
		self.rush_off = None
		self.recv_off = None

		self.qb = None
		self.rb = None
		self.wr = None

		self.win_pct = None

	def set_team_stat(self, col_name, rank):
		if col_name == 'pass_def':
			self.pass_def = rank
		elif col_name == 'rush_def':
			self.rush_def = rank
		else:
			raise Exception("Wrong column name")

	def set_player_stat(self, col_name, rank, player):
		if getattr(self, col_name) is None:
			if col_name == 'pass_off':
				self.pass_off = rank
				self.qb = player
			elif col_name == 'rush_off':
				self.rush_off = rank
				self.rb = player
			elif col_name == 'recv_off':
				self.recv_off = rank
				self.wr = player
			else:
				raise Exception("Wrong column name")

	def set_win_pct(self, win_pct):
		if self.win_pct is None:
			self.win_pct = win_pct

	def __str__(self):
		return self.team_name + \
		      "\n    Win %: " + str(self.win_pct) + \
		      "\n    Pass DEF: " + str(self.pass_def) + \
		      "\n    Rush DEF: " + str(self.rush_def) + \
		      "\n    Pass_OFF: " + str(self.pass_off) + \
		      "\n    Rush OFF: " + str(self.rush_off) + \
		      "\n    Recv OFF: " + str(self.recv_off)


class Matchup:
	def __init__(self, off_team, def_team, is_off_at_home):
		self.off_team = off_team
		self.def_team = def_team
		self.is_off_at_home = is_off_at_home

		win_pct_diff = off_team.win_pct - def_team.win_pct
		self.pass_score = calc_score(off_team.pass_off, def_team.pass_def, is_off_at_home, win_pct_diff)
		self.rush_score = calc_score(off_team.rush_off, def_team.rush_def, is_off_at_home, win_pct_diff)
		self.recv_score = calc_score(off_team.recv_off, def_team.pass_def, is_off_at_home, win_pct_diff)

	def qb(self):
		return self.off_team.qb

	def rb(self):
		return self.off_team.rb

	def wr(self):
		return self.off_team.wr

	def pass_str(self):
		return "\n    Pass Score: " +  str(self.pass_score) + \
				" (" + str(self.off_team.pass_off) + " vs " + str(self.def_team.pass_def) + ")"

	def rush_str(self):
		return "\n    Rush Score: " +  str(self.rush_score) + \
			   		" (" + str(self.off_team.rush_off) + " vs " + str(self.def_team.rush_def) + ")"

	def recv_str(self):
		return "\n    Recv Score: " +  str(self.recv_score) + \
			   		" (" + str(self.off_team.recv_off) + " vs " + str(self.def_team.pass_def) + ")"

	def print_base(self):
		if self.is_off_at_home:
			return self.off_team.team_abbr + " O (H) vs. " + self.def_team.team_abbr + " D"
		else:
			return self.off_team.team_abbr + " O vs. " + self.def_team.team_abbr + " D (H)"

	def print_pass(self):
		return self.print_base() + self.pass_str()

	def print_rush(self):
		return self.print_base() + self.rush_str()

	def print_recv(self):
		return self.print_base() + self.recv_str()

	def __str__(self):
		return self.print_base() + self.pass_str() + self.rush_str() + self.recv_str()
			   	

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
				rank = 33-int(row[0])
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

def compare_pass(visit_team, home_team, teams):
	pass 

def compare_rush(visit_team, home_team, teams):
	visit_rush_off = teams[visit_team].rush_off
	visit_rush_def = teams[visit_team].rush_def
	home_rush_off = teams[home_team].rush_off
	home_rush_def = teams[home_team].rush_def

	print visit_rush_off[0], home_rush_def
	print home_rush_off[0], visit_rush_def


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
		matchups.append(Matchup(visit, home, False))
		matchups.append(Matchup(home, visit, True))

	pass_mismatch = sorted(matchups, key=operator.attrgetter('pass_score'))
	rush_mismatch = sorted(matchups, key=operator.attrgetter('rush_score'))
	recv_mismatch = sorted(matchups, key=operator.attrgetter('recv_score'))

	print "=============== PASSING MISMATCHES ==============="
	rank = 1
	for matchup in pass_mismatch[:10]:
		print str(rank) + ') ' + matchup.print_pass()
		print "    " + matchup.qb()
		rank += 1

	print "=============== RUSHING MISMATCHES ==============="
	rank = 1
	for matchup in rush_mismatch[:10]:
		print str(rank) + ') ' + matchup.print_rush()
		print "    " + matchup.rb()
		rank += 1

	print "=============== RECEIVING MISMATCHES ==============="
	rank = 1
	for matchup in recv_mismatch[:10]:
		print str(rank) + ') ' + matchup.print_recv()
		print "    " + matchup.wr()
		rank += 1

