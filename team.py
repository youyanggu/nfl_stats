"""
Team class for each NFL team.

@author: Youyang Gu

"""

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