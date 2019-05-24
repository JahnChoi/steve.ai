import math
from past.utils import old_div
import actions
import time

try:
    from malmo import MalmoPython
except:
    import MalmoPython

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

    # ******DISCRETE WORLD SIZE*****
    # AGENT MOVES DISCRETELY - round locations
    # ZOMBIE MOVES DISCRETELY / IS STATIONARY - round
    # ADD ZOMBIE POSITION TO INPUTS
    # add sleeps for discrete time
    # figure out reward structure: ++health, --health, --time
    # if zombie is dead, end loop


class Steve(object):
    def __init__(self):
        print("creating new steve.ai")
        self.target = None
        self.entities = None

    def master_lock(self, ob, agent_host):
        agent_info = (ob.get(u'XPos', 0), ob.get(u'YPos', 0), ob.get(u'ZPos', 0))
        self.get_mob_loc(ob)
        if (self.check_entities == False):
            return
        self.closest_enemy(agent_info, self.entities)
        target_yaw, target_pitch = self.calcYawAndPitchToMob(self.entities[self.target], agent_info[0], agent_info[1], agent_info[2], 1.0)
        pointing = self.lock_on(agent_host, ob, target_pitch, target_yaw, 5)


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
            print(ent["name"])
            mob_id = ent['id']
            try:
                entities[mob_id] = (ent['x'], ent['y'], ent['z'], ent['life'])
            except:
                entities[mob_id] = (ent['x'], ent['y'], ent['z'], 0)
                print("key error caught")
        self.entities = entities

    def closest_enemy(self, agent, entities):
        mob_id = ""
        dist = 10000
        for mobs in entities.keys():
            new_dist = self.calculate_distance(agent, entities[mobs])
            if (dist > new_dist):
                mob_id = mobs
                dist = new_dist
        self.target = mob_id

    def calculate_distance(self, agent, mob):
        """Takes the agent and mob's location and calculates distance"""
        return math.sqrt((agent[0] - mob[0]) ** 2 + (agent[2] - mob[2]) ** 2)

    def perform_action(self, agent_host, action):
        if action == actions.MOVE_LEFT:
            print("moving left")
            agent_host.sendCommand("strafe -1")
            agent_host.sendCommand("strafe 0")
        elif action == actions.MOVE_RIGHT:
            print("moving right")
            agent_host.sendCommand("strafe 1")
            agent_host.sendCommand("strafe 0")
        elif action == actions.MOVE_FORWARD:
            print("moving forward")
            agent_host.sendCommand("move 1")
            agent_host.sendCommand("move 0")
        elif action == actions.MOVE_BACKWARD:
            print("moving backward")
            agent_host.sendCommand("move -1")
            agent_host.sendCommand("move 0")
        elif action == actions.STRIKE:
            print("striking")
            agent_host.sendCommand("hotbar.1 1")
            agent_host.sendCommand("hotbar.1 0")
            agent_host.sendCommand("attack 1")
            agent_host.sendCommand("attack 0")
        elif action == actions.BLOCK:
            print("blocking")
            agent_host.sendCommand("hotbar.2 1")
            agent_host.sendCommand("hotbar.2 0")
            agent_host.sendCommand("use 1")
            time.sleep(float(config.get('DEFAULT', 'TIME_STEP')))
            # time.sleep(1)
            agent_host.sendCommand("use 0")

        elif action == actions.JUMP:
            print("jumping")
            agent_host.sendCommand("jump 1")
            agent_host.sendCommand("jump 0")
        else:
            print("INVALID ACTION: " + str(action))

        # return new state, reward, and whether mission is done

    def get_state(self, ob, time_alive):
        ''' 0: Life
            1: Time Alive
            2: Mobs Killed
            3: Agent X
            4: Agent Z
            5: Target Life
            6: Target X
            7: Target Z'''
        if (self.check_entities == False):
            return
        target_health = self.entities[self.target][3]
        target_x, target_z = self.entities[self.target][0], self.entities[self.target][2]
        return [float(round(ob["Life"])), float(time_alive), float(ob["MobsKilled"]), float(round(ob["XPos"])),
                float(round(ob["ZPos"])), float(round(target_health)), float(round(target_x)), 
                float(round(target_z))]

    def check_entities(self):
        if (len(self.entities) < 1):
            return False
        else if (self.target != None && not in self.entities.keys()):
            return False
        return True
