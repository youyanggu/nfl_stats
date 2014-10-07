"""
Matchup Class, between an offense and a defense.

@author: Youyang Gu

"""

class Matchup:
	def __init__(self, off_team, def_team, is_off_at_home, week):
		self.off_team = off_team
		self.def_team = def_team
		self.is_off_at_home = is_off_at_home
		self.week = week

		self.win_pct_diff = off_team.win_pct - def_team.win_pct
		self.pass_score = self.calc_score(off_team.pass_off, def_team.pass_def)
		self.rush_score = self.calc_score(off_team.rush_off, def_team.rush_def)
		self.recv_score = self.calc_score(off_team.recv_off, def_team.pass_def)


	def calc_score(self, off_rank, def_rank):
		score = (def_rank - off_rank) * 1.0 / (off_rank + 4)
		# Home field advantage
		if not self.is_off_at_home:
			score -= abs(score)*0.1
		# Better team advantage
		score += self.win_pct_diff*(self.week / 10.0)
		return round(score, 2)

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