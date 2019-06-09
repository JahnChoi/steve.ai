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
state_size = int(config.get('DEFAULT', 'STATE_SIZE'))
action_size = int(config.get('DEFAULT', 'ACTION_SIZE'))
time_multiplier = int(config.get('DEFAULT', 'TIME_MULTIPLIER'))
nn = DQNAgent(state_size, action_size)
done = False
batch_size = int(config.get('DEFAULT', 'BATCH_SIZE'))
CLEARS = 0
MAX_SUCCESS_RATE = 0
GRAPH = live_graph.Graph()
REWARDS_DICT = {}
ALL_REWARDS = []
timestep = 0

# command line arguments
try:
    arg_check = sys.argv[1].lower()  # using arguments from command line
    if (arg_check not in ["zombie", "skeleton", "spider", "giant"]):
        print("\nInvalid mob type, defaulting to 1 zombie")
        mob_type = 'zombie'
        mob_number = 1
    else:
        mob_type = sys.argv[1]
        if (len(sys.argv) > 2):
            mob_number = int(sys.argv[2])
        else:
            mob_number = 1
        print(("\nTRAINING AGENT ON {} {}(S)").format(mob_number, mob_type.upper()))
except:
    print("\nError in argument parameters. Defaulting to 1 zombie")
    mob_type = 'zombie'
    mob_number = 1

nn_save = ""  # loading up previous save model if possible
if (len(sys.argv) > 3):
    # try:
    nn_save = ("save/{}.h5").format(sys.argv[3])
    nn.load(nn_save)
    print("Save Model successfully imported")
    # except:
    #     e = sys.exc_info()[0]
    #     print(e)
    #     print("Save model not found. Training new agent")
    #     nn_save = ("save/{}.h5").format(sys.argv[3])
    #     del nn
    #     nn = DQNAgent(state_size, action_size)  # need to restablish nn because load failed
else:
    nn_save = "save/ddqn-status-defaults-save.h5"

# starting training loop
for repeat in range(EPISODES):
    print('EPISODE: ', repeat)
    print("episode: {}/{}, score: {}, e: {:.2}"
          .format(repeat, EPISODES, time, nn.epsilon))

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
                time.sleep(1 / time_multiplier)

    # Loop until mission starts:
    print("Waiting for the mission to start ", end=' ')
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Starting Mission Error:", error.text)

    # Disable natural healing
    agent_host.sendCommand('chat /gamerule naturalRegeneration false')

    if repeat > 0:
        agent_host.sendCommand('chat /kill @e[type=!minecraft:player]')

    time.sleep(1 / time_multiplier)
    while len(world_state.observations) == 0:
        world_state = agent_host.getWorldState()
    world_state_txt = world_state.observations[-1].text
    world_state_json = json.loads(world_state_txt)
    agent_name = world_state_json['Name']

    agent_host.sendCommand("chat /replaceitem entity " + agent_name + " slot.weapon.offhand minecraft:shield")

    time.sleep(1 / time_multiplier)

    print()
    print("Mission running ", end=' ')

    agent_host.sendCommand('chat EPISODE: {}'.format(repeat))
    agent_host.sendCommand('chat SUCCESS RATE: {}'.format((CLEARS / (repeat + 1)) * 100))

    x = world_state_json['XPos']
    y = world_state_json['YPos']
    z = world_state_json['ZPos']
    for i in range(mob_number):
        spawn_command = 'chat /summon {} {} {} {}'.format(mob_type, x - 8, y, z - 8 + (i * 2))
        if mob_type == 'zombie':
            spawn_command += ' {IsBaby:0}'
        agent_host.sendCommand(spawn_command)

    time.sleep(1 / time_multiplier)

    steve = steve_agent.Steve(mob_type)
    # Loop until mission ends:

    # keep track if we've seeded the initial state
    have_initial_state = 0

    mobs_left = mob_number
    rewards = []
    while world_state.is_mission_running:
        time.sleep(float(config.get('DEFAULT', 'TIME_STEP')) / time_multiplier)  # discretize time/actions
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("World State Error:", error.text)

        if world_state.number_of_observations_since_last_state > 0:

            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            time_alive = int(time.time() - time_start)
            lock_on = steve.master_lock(ob, agent_host)

            try:
                state = steve.get_state(ob, time_alive)
            except KeyError as k:
                print("Key Error:", k)
                CLEARS += 1
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
            steve.perform_action(agent_host, action)  # send action to malmo
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            steve.get_mob_loc(ob)  # update entities in steve
            next_state = steve.get_state(ob, time_alive)

            if (repeat == 5000):
                done = True
            else:
                done = False

            lock_on = steve.master_lock(ob, agent_host)

            if next_state[0] == 0:  # steve dying
                player_bonus = -500
            else:
                player_bonus = 0

            if (len(steve.entities.keys()) < mobs_left):  # steve getting kills
                kill_bonus = 400  # this method does not work, need a new method
                mobs_left -= 1
                if nn.epsilon > nn.epsilon_min:
                    nn.epsilon *= nn.epsilon_decay
            else:
                kill_bonus = 0

            if next_state[4] == 0:  # steve clearing arena
                arena_bonus = 500
                CLEARS += 1
                if nn.epsilon > nn.epsilon_min:
                    nn.epsilon *= nn.epsilon_decay
            else:
                arena_bonus = 0

            steve_loc = (next_state[2], 0, next_state[3])
            mob_distance = (steve.calculate_distance(steve_loc, steve.entities[steve.target]) + 3)
            reward = ((next_state[0] * 20) - (next_state[4] * 200) - (time_alive * 4) + player_bonus +
                      kill_bonus + arena_bonus - (mob_distance * 5))  # get reward

            rewards.append(reward)
            ALL_REWARDS.append(reward)
            GRAPH.animate_episode(range(0, timestep + 1), ALL_REWARDS)
            timestep += 1
            next_state = np.reshape(next_state, [1, state_size])
            nn.remember(state, action, reward, next_state, done)
            state = next_state
            if done:
                print("DONE TRIGGERED")
                nn.update_target_model()
                print("episode: {}/{}, score: {}, e: {:.2}"
                      .format(repeat, EPISODES, time, nn.epsilon))
                break
            if len(nn.memory) > batch_size:  # it will decay eps
                nn.replay(batch_size)
            if (arena_bonus != 0):  # just some quick spaghetti to get us out of NN loop after cleared arena hehe
                agent_host.sendCommand("quit")
                break

    if repeat % 10 == 0:
        print('Saving file to {}'.format(nn_save))
        nn.save(nn_save)

        # MAIN NN LOGIC

    REWARDS_DICT[repeat] = sum(rewards) / len(rewards)
    GRAPH.animate(list(REWARDS_DICT.keys()), list(REWARDS_DICT.values()))

    print('SUCCESS RATE: {} / {} = {}%'.format(CLEARS, repeat + 1, (CLEARS / (repeat + 1)) * 100))
    print("Mission ended")
    print()
    # Mission has ended.
