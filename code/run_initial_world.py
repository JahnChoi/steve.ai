import os
import sys
import time
try:
    from malmo import MalmoPython
except:
    import MalmoPython
import steve_agent


# Create default Malmo objects:

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse(sys.argv)
except RuntimeError as e:
    print('ERROR:', e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)

missionXML = open('world.xml', 'r')
my_mission = MalmoPython.MissionSpec(missionXML.read(), True)
my_mission_record = MalmoPython.MissionRecordSpec()

my_client_pool = MalmoPython.ClientPool()
my_client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10000))

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        agent_host.startMission(my_mission, my_client_pool, my_mission_record, 0, "test")
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print("Error starting mission:", e)
            exit(1)
        else:
            time.sleep(2)


# Loop until mission starts:
print("Waiting for the mission to start ", end=' ')
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:",error.text)

print()
print("Mission running ", end=' ')


# Loop until mission ends:
while world_state.is_mission_running:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:",error.text)

    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        ob = json.loads(msg)
        steve = Steve()
        #all entity_info in a tuple (x, y, z)
        agent_info = (ob.get(u'Xpos', 0), ob.get(u'Ypos', 0), ob.get(u'Zpos', 0)) 
        entities = steve.get_mob_loc(ob) 
        target = steve.closest_enemy(agent_info, entities)
        #zombie mob height is 1.9 LMAO 
        target_yaw, target_pitch = steve.calcYawAndPitchToMob(target, agent[0], agent[1], agent[2], 1.9) 
        pointing = steve.lock_on(agent_host, ob, target_pitch, target_yaw, 0.5)

print()
print("Mission ended")
# Mission has ended.
