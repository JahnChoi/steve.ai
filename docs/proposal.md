---
layout: default
title:  Proposal
---


**Summary**:

We plan to train an agent that will be proficient in combat against the in-game Mobs from Minecraft. Our agent will spawn on an infinite plane equipped with a sword. After a successful attempt, our agent will then be transferred to another infinite world with a fresh Mob to kill. The agent will be trained to effectively combat against singular Mobs at first and then progress to groups. The agent will consume its location and location/type of local Mobs. It will also consider the type of weapon in its arsenal and delta time since last enemy attack. The agent will produce a set of actions to combat the Mobs. These could include striking, walking, running, parrying, and jumping. It's reward structure will involve positive reward for killing enemies and negative reward for passage of time and death.

**AI/ML Algorithms**:

We plan to use a form of Q-Learning. We will implement our Q-Learning approach using a neural network. Currently, our program will utilize Keras and TensorFlow python libraries to support a Reinforcement Learning algorithm.

**Evaluation**:

We will evaluate the success of our agent using the function (number of Mobs killed / time taken for all kills) as well as whether our agent survives the encounter. This will ensure our agent will be killing Mobs with maximum efficiency. As a baseline, we will personally attempt fights with in game Mobs and measure our efficiency in comparison to the agent. We hope our agent will be at least 25% more efficient than our attempts.

The sanity cases our agent will be subjected to include its ability to neutralize single Mobs within a reasonable timeframe. We will graph the evaluation function over time/generations of our model to verify that our model is improving its abilities. Our moonshot will be an agent that is capable of adapting to fight any mob type in Minecraft with high efficiency and multiple strategic options.

**Appointment**:

Our appointment is set up for Friday April 26th at 10am in DBH 4204.