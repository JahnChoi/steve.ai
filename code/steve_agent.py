from Malmo import MalmoPython
import math

class Steve(object):
	def __init__(self, alpha = 0.3, gamma = 1, n = 1):
		self.eps = 0.2
		self.q_table = {}
		self.alpha = alpha
		self.gamam = gamma 
		self.n = n

	def get_mob_loc(agent_host):
		"""gets the locations of all the entities in world state"""
		entities = {}
		while True:
			world_state = agent_host.getWorldState()
			if world_state.number_of_observations_since_last_state > 0:
				msg = world_state.observations[-1].text
				ob = json.loads(msg)
				for ent in ob['entities']:
					name = end['name']
					entities[name] = (ent['x'], ent['z'], ent['yaw'])
				return entities

	def lock_on(self, mob):
		"""makes sure Steve locks onto closest mob"""
		agent = entities['Steve']
		'''need to figure out how to calculate YAW for looking at mob'''

	def closest_enemy(self, entities):
		agent = entities['Steve']
		mob_name = 'Steve'
		dist = 10000
		for mobs in entities.keys():
			new_dist = calculate_distance(agent, entities[mobs])
			if (dist > new_dist):
				mob_name = mobs
				dist = new_dist
		return mob_name

	def calculate_distance(agent, mob):
		"""Takes the agent and mob's location and calculates distance"""
		return math.sqrt((agent[0] - mob[0])**2 + (agent[1] - mob[1])**2)

