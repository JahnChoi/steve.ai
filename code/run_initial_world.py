import sys
import time

try:
    from malmo import MalmoPython
except:
    import MalmoPython
import steve_agent
import json

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

with open('world.xml', 'r') as file:
    missionXML = file.read()

my_client_pool = MalmoPython.ClientPool()
my_client_pool.add(MalmoPython.ClientInfo('127.0.0.1', 10000))

EPISODES = 5000

for repeat in range(EPISODES):
    my_mission = MalmoPython.MissionSpec(missionXML, True)
    my_mission_record = MalmoPython.MissionRecordSpec()

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
        time.sleep(2)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)

    world_state_txt = world_state.observations[-1].text
    world_state_json = json.loads(world_state_txt)
    if len(world_state_json['entities']) > 2:
        agent_host.sendCommand('chat /kill @e[type=Zombie,c=1]')

    print()
    print("Mission running ", end=' ')

    # Loop until mission ends:
    while world_state.is_mission_running:
        print(".", end="")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)

    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        ob = json.loads(msg)
        steve = steve_agent.Steve()
        state = steve.get_state(ob)
        print(state)
        # all entity_info in a tuple (x, y, z)
        agent_info = (ob.get(u'XPos', 0), ob.get(u'YPos', 0), ob.get(u'ZPos', 0))
        entities = steve.get_mob_loc(ob)
        target = steve.closest_enemy(agent_info, entities)
        # zombie mob height is 1.9 LMAO
        target_yaw, target_pitch = steve.calcYawAndPitchToMob(target, agent_info[0], agent_info[1], agent_info[2], 1.9)
        pointing = steve.lock_on(agent_host, ob, target_pitch, target_yaw, 5)

    print()
    print("Mission ended")
    # Mission has ended.
