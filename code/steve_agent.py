import math
from past.utils import old_div
import actions

try:
    from malmo import MalmoPython
except:
    import MalmoPython


class Steve(object):
    def __init__(self):
        print("creating new steve.ai")

    def lock_on(self, agent_host, ob, target_pitch, target_yaw, threshhold):
        pitch = ob.get(u'Pitch', 0)
        yaw = ob.get(u'Yaw', 0)
        delta_yaw = self.angvel(target_yaw, yaw, 25.0)
        delta_pitch = self.angvel(target_pitch, pitch, 25.0)
        agent_host.sendCommand("turn " + str(delta_yaw))
        agent_host.sendCommand("pitch " + str(delta_pitch))
        # if abs(pitch - target_pitch) + abs(yaw - target_yaw) < threshhold:
        #     agent_host.sendCommand("turn 0")
        #     agent_host.sendCommand("pitch 0")
        #     return True
        return False

    def angvel(self, target, current, scale):
        delta = target - current
        while delta < -180:
            delta += 360
        while delta > 180:
            delta -= 360
        return (old_div(2.0, (1.0 + math.exp(old_div(-delta, scale))))) - 1.0

    def calcYawAndPitchToMob(self, target, x, y, z, target_height):
        dx = target[0] - x
        dz = target[2] - z
        yaw = -180 * math.atan2(dx, dz) / math.pi
        distance = math.sqrt(dx * dx + dz * dz)
        pitch = math.atan2(((y + 1.625) - (target[1] + target_height * 0.9)), distance) * 180.0 / math.pi
        return yaw, pitch

    def get_mob_loc(self, ob):
        """gets the locations of all the entities in world state"""
        entities = {}
        for ent in ob["entities"]:
            if (ent["name"] == "175Project"):
                continue
            mob_id = ent['id']
            entities[mob_id] = (ent['x'], ent['y'], ent['z'])
        return entities

    def closest_enemy(self, agent, entities):
        mob_name = ""
        dist = 10000
        for mobs in entities.keys():
            new_dist = self.calculate_distance(agent, entities[mobs])
            if (dist > new_dist):
                mob_name = mobs
                dist = new_dist
        return entities[mob_name]

    def calculate_distance(self, agent, mob):
        """Takes the agent and mob's location and calculates distance"""
        return math.sqrt((agent[0] - mob[0]) ** 2 + (agent[2] - mob[2]) ** 2)

    def perform_action(self, agent_host, action):
        if action == actions.MOVE_LEFT:
            print("moving left")
            agent_host.sendCommand("left")
        elif action == actions.MOVE_RIGHT:
            print("moving right")
            agent_host.sendCommand("right")
        elif action == actions.MOVE_FORWARD:
            print("moving forward")
            agent_host.sendCommand("forward")
        elif action == actions.MOVE_BACKWARD:
            print("moving backward")
            agent_host.sendCommand("backward")
        elif action == actions.STRIKE:
            print("striking")
            agent_host.sendCommand("attack 1")
        elif action == actions.BLOCK:
            print("blocking")
            agent_host.sendCommand("use 1")
        elif actions == actions.JUMP:
            print("jumping")
            agent_host.sendCommand("jump 1")

        else:
            print("INVALID ACTION")

        # return new state, reward, and whether mission is done

    def get_state(self, ob):
        ''' 0: Life
            1: Damage Taken
            2: Damange Dealt
            3: Mobs KIlled
            4: Time Alive
            5: Total time
            6: Xpos
            7: Zpos '''
        return [ob["Life"], ob["DamageTaken"], ob["DamageDealt"], ob["MobsKilled"], ob["TimeAlive"], ob["XPos"],
                ob["YPos"]]
