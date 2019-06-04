import sys
import time

try:
    from malmo import MalmoPython
except:
    import MalmoPython
import steve_agent
import live_graph
import json
import configparser
import numpy as np
from ddqn import DQNAgent

config = configparser.ConfigParser()
config.read('config.ini')

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

EPISODES = int(config.get('DEFAULT', 'EPISODES'))
state_size =  int(config.get('DEFAULT', 'STATE_SIZE'))
action_size =  int(config.get('DEFAULT', 'ACTION_SIZE'))
time_multiplier = int(config.get('DEFAULT', 'TIME_MULTIPLIER'))
nn = DQNAgent(state_size, action_size)
done = False
batch_size = int(config.get('DEFAULT', 'BATCH_SIZE'))
KILLS = 0
MAX_SUCCESS_RATE = 0
GRAPH = live_graph.Graph()
REWARDS_DICT = {}

try:
	arg_check = sys.argv[1].lower()
	if (arg_check not in ["zombie", "creeper", "slime", "skeleton", 
		"spider", "enderman", "witch", "blaze"]):
		print("Invalid mob type, defaulting to 1 zombie")
		mob_type = 'zombie' 
		mob_number = 1
	else:
		mob_type = sys.argv[1]
		mob_number = int(sys.argv[2])
		print(("TRAINING ON AGENT ON {} {}s").format(mob_number, mob_type))
except:
	print("Error in argument parameters. Defaulting to 1 zombie")
	mob_type = 'zombie' 
	mob_number = 1

# nn.load('Epsilon-0.1,Gamma-0.3,LR-0.75/ddqn-save-220episodes.h5')
# print('MODEL LOADED')

for repeat in range(EPISODES):
    print('EPISODE: ', repeat)

    time_start = time.time()
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
                time.sleep(1/time_multiplier)

    # Loop until mission starts:
    print("Waiting for the mission to start ", end=' ')
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)

    if repeat > 0:
        agent_host.sendCommand('chat /kill @e[type=!minecraft:player]')

    time.sleep(1/time_multiplier)
    while len(world_state.observations) == 0:
        world_state = agent_host.getWorldState()
    world_state_txt = world_state.observations[-1].text
    world_state_json = json.loads(world_state_txt)
    agent_name = world_state_json['Name']

    agent_host.sendCommand("chat /replaceitem entity " + agent_name + " slot.weapon.offhand minecraft:shield")

    time.sleep(1/time_multiplier)

    print()
    print("Mission running ", end=' ')

    agent_host.sendCommand('chat EPISODE: {}'.format(repeat))
    agent_host.sendCommand('chat SUCCESS RATE: {}'.format((KILLS/(repeat+1))*100))

    x = world_state_json['XPos']
    y = world_state_json['YPos']
    z = world_state_json['ZPos']
    for i in range(mob_number):
        agent_host.sendCommand('chat /summon {} {} {} {}'.format(mob_type,x-8, y, z-8+(i*2)))

    time.sleep(1/time_multiplier)

    steve = steve_agent.Steve(mob_type)
    # Loop until mission ends:

    # keep track if we've seeded the initial state
    have_initial_state = 0

    rewards = []
    while world_state.is_mission_running:
        time.sleep(float(config.get('DEFAULT', 'TIME_STEP'))/time_multiplier) # discretize time/actions
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)

        if world_state.number_of_observations_since_last_state > 0:

            msg = world_state.observations[-1].text
            ob = json.loads(msg)

            time_alive = int(time.time() - time_start)
            steve.get_mob_loc(ob)
            steve.closest_enemy((ob.get(u'XPos', 0), ob.get(u'YPos', 0), ob.get(u'ZPos', 0)), steve.entities)

            try:
                state = steve.get_state(ob, time_alive)
            except KeyError as k:
            	print(k)
            	KILLS += 1
            	if nn.epsilon > nn.epsilon_min:
                	nn.epsilon *= nn.epsilon_decay
            	agent_host.sendCommand("quit")
            	break

            # MAIN NN LOGIC
            # check if we've seeded initial state just for the first time
            if have_initial_state == 0:
                state = steve.get_state(ob, time_alive)
                have_initial_state = 1

            state = np.reshape(state, [1, state_size])
            action = nn.act(state)
            steve.perform_action(agent_host, action) # send action to malmo
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            next_state = steve.get_state(ob, time_alive)

            if (repeat == 5000):
                done = True
            else:
                done = False

            # if zombie is dead, quit mission and break nn loop
            if next_state[4] == 0 and len(ob['entities']) < 3:
                KILLS += 1
                if nn.epsilon > nn.epsilon_min:
                    nn.epsilon *= nn.epsilon_decay
                agent_host.sendCommand("quit")
                break

            lock_on = steve.master_lock(ob, agent_host)

            if next_state[0] == 0:
                player_bonus = -10000000
            else:
                player_bonus = 0

            if next_state[4] == 0:
                kill_bonus = 10000000
            else:
                kill_bonus = 0

            reward = next_state[0]**2 - next_state[4]**5 - time_alive**2 + player_bonus + kill_bonus # get reward
            rewards.append(reward)
            # print(reward)
            next_state = np.reshape(next_state, [1, state_size])
            # reward = reward if not done else -10 ?
            nn.remember(state, action, reward, next_state, done)
            state = next_state
            if done:
                nn.update_target_model()
                print("episode: {}/{}, score: {}, e: {:.2}"
                      .format(repeat, EPISODES, time, nn.epsilon))
                break
            if len(nn.memory) > batch_size:
                nn.replay(batch_size)

    if (KILLS/(repeat+1))*100 > MAX_SUCCESS_RATE:
        MAX_SUCCESS_RATE = (KILLS/(repeat+1))*100
        nn.save('ddqn-save.h5')

            # MAIN NN LOGIC

    print(REWARDS_DICT)
    REWARDS_DICT[repeat] = sum(rewards)/len(rewards)
    GRAPH.animate(REWARDS_DICT.keys(), REWARDS_DICT.values())

    print('SUCCESS RATE: {} / {} = {}%'.format(KILLS, repeat+1, (KILLS/(repeat+1))*100))
    print("Mission ended")
    print()
    # Mission has ended.
