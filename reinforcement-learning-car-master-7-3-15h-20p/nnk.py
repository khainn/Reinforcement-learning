import random
import math
import numpy as np

import pygame
from pygame.color import THECOLORS

import pymunk
from pymunk.vec2d import Vec2d
from pymunk.pygame_util import draw

from nn import neural_net, LossHistory

readings = []
replay = []

model = neural_net(5, [128, 128])

#def train_net(model, params):
x = 100
#readings.append(random.randint(0,40))
readings.append(-30)
readings.append(10)
readings.append(40)
x += 20
normalized_readings = [(x-20.0)/20.0 for x in readings] 
state = np.array([normalized_readings])

for i in range(2):
    readings = []
    readings.append(-20)
    readings.append(-5)
    readings.append(10)
    
    x += 20
    normalized_readings = [(x-20.0)/20.0 for x in readings] 
    orientation = Vec2d(1, 0).rotated(0.2)
    distance = 569

    normalized_readings.append(orientation)
    normalized_readings.append(distance)
    new_state = np.array([normalized_readings])

    reward = random.randint(-500, 500)
    action = random.randint(0, 3)

    replay.append((state, action, reward, new_state))
    state = new_state

#replay = [([-0.9 -0.5 0.7], 1, -300, [-0.8 0.4 0.3]), ([-0.6 -0.4 0.7], 2, 200, [-0.2 0.1 0.3]), ([-0.8 -0.1 0.4], 1, 50, [-0.4 0.1 0.2])]

# mb_len = len(replay)

# old_states = np.zeros(shape=(mb_len, 5))
# actions = np.zeros(shape=(mb_len,))
# rewards = np.zeros(shape=(mb_len,))
# new_states = np.zeros(shape=(mb_len, 5))

# for i, m in enumerate(replay):
#     old_state_m, action_m, reward_m, new_state_m = m
#     old_states[i, :] = old_state_m[...]
#     actions[i] = action_m
#     rewards[i] = reward_m
#     new_states[i, :] = new_state_m[...]

# old_qvals = model.predict(old_states, batch_size=mb_len)
# new_qvals = model.predict(new_states, batch_size=mb_len)

#return old_qvals
# maxQs = np.max(old_qvals, axis=1)

#print(model.summary())
print(state)
# print(new_states)
# print(new_qvals)

