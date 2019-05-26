---
layout: default
title:  Status
---

**Video Summary**:

<iframe width="560" height="315" src="https://www.youtube.com/embed/7KdLfg8sPq4" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

**Summary**:

Our goal is to train an agent in Minecraft to be efficient in combat against in game mobs. The agent will begin with a sword and shield, and will be placed in a glowstone arena surrounded by lava. The agent will utilize a deep q learning neural network to determine its next move in a given situation. We begin by training our agent against a singular mob-type, the zombie. The agent’s reward will be determined after every action by recording the agent’s health, the enemy’ health, agent position, enemy position, and the time passed since mission start. An effective agent would be classified as an agent that is able to slay the enemy quickly while also reducing the amount of damage it takes. To do this, the agent will have the option to move, strafe, jump, attack with a sword, and block with a shield.

**Approach**:

Our approach involves consuming the world state (player_health, time_alive, player_x_pos, player_z_pos, zombie_health, zombie_x_pos, zombie_z_pos), and feeding this state into our deep q network. The agent then performs an action based on the q network’s suggestion. The q network decides to perform an action randomly at a low probability, or alternatively, an action that is chosen from its memory / by the neural network if it is less familiar with the given state.<br/>
Once the selected action has been performed on the environment, the agent polls for the new state and a reward. The new state, reward, old state, and action performed are saved to the agent’s memory for reference when experiencing a similar state in the future. This feedback loop continues until the agent either kills the enemy, dies, or the mission times out. Upon death, extra reward is either awarded or subtracted in order to emphasize the importance of these states.

**Evaluation**:

Every action taken by our agent would result in a change somewhere in the environment,  whether it be a change in position or a change in health values. Due to this, we decided to evaluate our agent after every single move in order for our agent to learn quickly and on the spot. The evaluation formula used after each action is: player_health^2 - zombie_health^5 - time_alive^2 + player_living_at_end_bonus + zombie_killed_bonus. This formula will incentivize the agent to actively partake in combat in order to reduce the negative effects of time_passed and maximize the positive effects of a reduced target_health. Using agent_health motivates the agent to try to avoid taking damage from the mob as well as have our agent utilize the shield to block incoming damage. The best outcome for the agent in each scenario would be to kill the mob as quickly as possible while maintaining full health. Our main method of evaluating the success of our model is through its success rate. This rate is calculated by measuring the total number of successful kills during the training period / the total count of training periods. We’ve found that our model in the current state is able to achieve 90%+ success rate in killing the enemy before death or timeout.

**Remaining Goals and Challenges**:

Our current model is limited in it’s optimization. We have not done a great amount of experimentation with hyper parameters or network setup / tuning. Our primary goal will be to increase the success rate of our model through tuning these parameters. Our next goal will be to incorporate different mob types into the arena, or even multiple mobs and perhaps generate multiple models that can be queried depending on the type of mob that the agent is faced with. We expect to face difficulty when attempting the leap from 1 mob type / enemy per training episode to multiple mob types or enemies per episode. We are not sure how the model will react in these situations, so we expect to face challenges here.

**Resources Used**:

For developing the environment our agent will be tasked in fighting in, we utilized python samples provided by Microsoft’s implementation of Malmo. We pulled examples from files such as mob_zoo.py and mob_fun.py to generate a flatworld, to equip our agent with weaponry, to spawn a zombie consistently, and to track a target consistently. For our deep q learning algorithm, we utilized Keras documentation and a tutorial provided in a blog by <a href="https://keon.io/deep-q-learning/?fbclid=IwAR20K1_C5dI6ngPzBs3dV7s8mSqnhnJI7FA-1-GQ8Y6raoN6HOk20dbKe1Y">Keon</a>. We examined how Keon set-up his neural network using keras and interacted with his game environment.