import math
from past.utils import old_div

try:
    from malmo import MalmoPython
except:
    import MalmoPython

class Steve(object):
	def __init__(self, alpha = 0.3, gamma = 1, n = 1):
		self.eps = 0.2
		self.q_table = {}
		self.alpha = alpha
		self.gamam = gamma 
		self.n = n

	def lock_on(self, agest_host, ob, target_pitch, target_yaw, threshhold):
		pitch = ob.get(u'Pitch', 0)
		yaw = ob.get(u'Yaw', 0)
		delta_yaw = angvel(target_yaw, yaw, 50.0)
		delta_pitch = angvel(target_pitch, pitch, 50.0)
		agent_host.sendCommand("turn " + str(delta_yaw))
		agent_host.sendCommand("pitch " + str(delta_pitch))
		if abs(pitch-target_pitch) + abs(yaw-target-yaw) < threshhold:
			agent_host.sendCommand("turn 0")
			agent_host.sendCommand("pitch 0")
			return True
		return False

	def angvel(self, target, current, scale):
		delta = target - current
		while delta < -180:
			delta += 360
		while delta > 180:
			delta -= 360
		return (old_div(2.0, (1.0 + math.exp(old_div(-delta,scale))))) - 1.0

	def calcYawAndPitchToMob(self, target, x, y, z, target_height):
		dx = target.x - x
		dz = target.z - z
		yaw = -180 * math.atan2(dx, dz) / math.pi
		distance = math.sqrt(dx * dx + dz * dz)
		pitch = math.atan2(((y + 1.625) - (target.y + target_height * 0.9)), distance) * 180.0/math.pi
		return yaw, pitch

	def get_mob_loc(self, ob):
		"""gets the locations of all the entities in world state"""
		entities = {}
		for ent in ob['entities']:
			name = ent['name']
			entities[name] = (ent['x'], ent['y'], ent['z'])
		return entities

	def closest_enemy(self, agent, entities):
		mob_name = 'Steve'
		dist = 10000
		for mobs in entities.keys():
			if (mobs == 'Steve'):
				continue
			new_dist = calculate_distance(agent, entities[mobs])
			if (dist > new_dist):
				mob_name = mobs
				dist = new_dist
		return entities[mob_name]

	def calculate_distance(self, agent, mob):
		"""Takes the agent and mob's location and calculates distance"""
		return math.sqrt((agent[0] - mob[0])**2 + (agent[2] - mob[2])**2)

