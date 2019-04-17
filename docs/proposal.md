---
layout: default
title:  Proposal
---


Summary:

We plan to train an agent that will be proficient in combat against the in-game Mobs from Minecraft. Our agent will begin inside a consistent fighting ring equipped with a bow and quiver as well as a sword. After a successful attempt, our agent will then be transferred to another prebuilt arena with a different type or group of mobs. The agent will be trained to effectively combat against singular Mobs at first and then progress to groups. The agent will consume the location and type of local mobs, as well as its own position and surroundings. It will also consider the types of weapons in it’s arsenal. The agent will produce a set of actions to combat the mobs. These could include shooting, striking, walking, running, parrying, and jumping.

AI/ML Algorithms:

We plan to use a form of Q-Learning. We will implement our Q-Learning approach using a neural network. Currently, our program will utilize Keras and TensorFlow python libraries to support a Reinforcement Learning algorithm.

Evaluation:

We will evaluate the success of our agent using the function (number of mobs killed / time taken for all kills) as well as whether our agent survives the encounter. This will ensure our agent will be killing enemy mobs with maximum efficiency and survive any encounter. As a baseline, we will personally attempt fights with in game Mobs and measure our efficiency in comparison to the agent. Each state and action that our agent encounters/produces will be logged for debugging and model improvement purposes. We hope our agent will be at least 25% more efficient than our attempts.
The sanity cases our agent will be subjected to include its ability to neutralize single Mobs within a reasonable timeframe. We will graph the evaluation function over time/generations of our model to verify our model’s fighting capabilities. We will also attempt to map out a live graph of our agent within the arena while it fights different types of mobs to fully analyze its capabilities. Our moonshot will be an agent that is 200% as effective as our human combat skills. Or, perhaps an agent that cannot be defeated by any reasonable number of Mobs.

Appointment:

Our appointment is set up for Friday April 26th at 10am in DBH 4204.