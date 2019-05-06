from Malmo import MalmoPython

class Steve(object):
	def __init__(self, alpha = 0.3, gamma = 1, n = 1):
		self.eps = 0.2
		self.q_table = {}
		self.alpha = alpha
		self.gamam = gamma 
		self.n = n
	