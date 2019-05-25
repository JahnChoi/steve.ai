import sys
import time

try:
    from malmo import MalmoPython
except:
    import MalmoPython
import steve_agent
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

EPISODES = 5000

state_size =  int(config.get('DEFAULT', 'STATE_SIZE'))
action_size =  int(config.get('DEFAULT', 'ACTION_SIZE'))
time_multiplier = int(config.get('DEFAULT', 'TIME_MULTIPLIER'))
nn = DQNAgent(state_size, action_size)
done = False
batch_size = int(config.get('DEFAULT', 'BATCH_SIZE'))

for repeat in range(EPISODES):
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
        print(".", end="")
        time.sleep(2/time_multiplier)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)

    time.sleep(2 / time_multiplier)
    world_state_txt = world_state.observations[-1].text
    world_state_json = json.loads(world_state_txt)

    # if len(world_state_json['entities']) > 2:
        # agent_host.sendCommand('chat /kill @e[type=Zombie,c=1]')
    agent_host.sendCommand('chat /kill @e[type=!minecraft:player]')

    time.sleep(1/time_multiplier)

    print()
    print("Mission running ", end=' ')

    x = world_state_json['XPos']
    y = world_state_json['YPos']
    z = world_state_json['ZPos']
    agent_host.sendCommand('chat /summon zombie {} {} {}'.format(x+15, y, z))

    time.sleep(1/time_multiplier)

    steve = steve_agent.Steve()
    # Loop until mission ends:

    # keep track if we've seeded the initial state
    have_initial_state = 0

    while world_state.is_mission_running:
        print(".", end="")
        time.sleep(float(config.get('DEFAULT', 'TIME_STEP'))/time_multiplier) # discretize time/actions
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)

        if world_state.number_of_observations_since_last_state > 0:
            # if zombie is dead, quit the mission and break nn loop
            if len(world_state_json['entities']) < 2:
                agent_host.sendCommand("quit")
                break

            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            lock_on = steve.master_lock(ob, agent_host)

            time_alive = int(time.time() - time_start)
            state = steve.get_state(ob, time_alive)

            print(state)


            # MAIN NN LOGIC
            # check if we've seeded initial state just for the first time
            if have_initial_state == 0:
                state = steve.get_state(ob, time_alive)
                have_initial_state = 1

            state = np.reshape(state, [1, state_size])
            action = nn.act(state)
            steve.perform_action(agent_host, action) # send action to malmo
            next_state = steve.get_state(ob, time_alive)

            if (repeat == 5000):
                done = True
                agent_host.sendCommand("quit")
            else:
                done = False

            # if zombie is dead, quit mission and break nn loop
            if next_state[5] == 0:
                agent_host.sendCommand("quit")
                break

            reward = next_state[0] - next_state[5] - time_alive  # get reward
            print(reward)
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
            # MAIN NN LOGIC

    print()
    print("Mission ended")
    # Mission has ended.
