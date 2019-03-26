import random
import math
import numpy as np

import pymunk
from pymunk.vec2d import Vec2d

import string

import sys
import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 9600)

goal_x = 10000
goal_y = 1000
car_x = 0
car_y = 0

class GameState:

    def __init__(self):

        self.crashed = False

        self.num_steps = 0
        self.last_steps = 0

    def frame_step(self, action):

        # global last_distance
        global goal_x
        global goal_y
        global car_x
        global car_y

        if action == 0:     #trai
            ser.write(b'0')
            time.sleep(0.5)
            readings, angle_car, car_move = self.get_sonar_readings()
            angle_car = self.go_around(angle_car)
        elif action == 1:   #phai
            ser.write(b'1')
            time.sleep(0.5)
            readings, angle_car, car_move = self.get_sonar_readings()
            angle_car = self.go_around(angle_car)
        elif action == 2:   #thang
            ser.write(b'2')  
            time.sleep(0.5)
            readings, angle_car, car_move = self.get_sonar_readings()
            car_x, car_y = self.go_straight(car_move, car_x, car_y, angle_car)

        distance = np.sqrt((car_x - goal_x)**2 + (car_y - goal_y)**2)
        orientate_goal = Vec2d(goal_x - car_x, goal_y - car_y)
        orientate_car = Vec2d(1, 0).rotated(angle_car)
        orientation = orientate_car.get_angle() - orientate_goal.angle()

        normalized_readings = [(x-20.0)/20.0 for x in readings]
        normalized_readings.append(orientation)
        normalized_readings.append(distance)
        state = np.array([normalized_readings])


        # Set the reward.
        if self.car_is_crashed(readings):
            self.crashed = True
            reward = -500
            self.recover_from_crash()
        else:
            reward = -5 + int(self.sum_readings(readings)/10)

        # if distance < last_distance:
        #     reward = 10
        #    reward = last_distance - distance
        # else:
        #     reward = distance - last_distance

        if distance < 10:
            goal_x = 10000 - goal_x
            reward = 500
#            reward = self.last_steps - self.num_steps # reward for reaching the objective faster than last round (may want to scale this)
            self.last_steps = self.num_steps 
            self.num_steps = 0

        self.num_steps += 1
        # last_distance = distance
        # time.sleep(0.5)

        return reward, state, distance

    def car_is_crashed(self, readings):
        if readings[0] <= 10 or readings[1] <= 10 or readings[2] <= 10:
            return True
        else:
            return False

    def recover_from_crash(self):
        """
        We hit something, so recover.
        """

        while self.crashed:
            self.crashed = False
            ser.write(b's')
            ser.write(b'1')
            time.sleep(0.5)
            ser.write(b's')
   
    def sum_readings(self, readings):
        """Sum the number of non-zero readings."""
        tot = 0
        for i in readings:
            tot += i
        return tot

    def get_sonar_readings(self):

        readings = []
        line = []
        cb1 = []
        cb2 = []
        cb3 = []
        angle_car = []
        encoder = []
        car_move = 0

        ser.write(b'r')
        
        i = 0
        flag = 1
        while flag:
            for c in ser.read():
                if c == 36:
                    i = i + 1
                if i == 1 and c != 36:
                    cb1.append(chr(c))
                if i == 2 and c != 36:
                    cb2.append(chr(c))
                if i == 3 and c != 36:
                    cb3.append(chr(c))
                if i == 4 and c != 36:
                    angle_car.append(chr(c))
                if i == 5 and c != 36:
                    encoder.append(chr(c))
                if i == 6 and c != 36:
                    flag = 0

        cb1 = int(''.join(cb1))       
        cb2 = int(''.join(cb2))
        cb3 = int(''.join(cb3))
        angle_car = int(''.join(angle_car))
        encoder = int(''.join(encoder))

        car_move = self.get_move(encoder)

        readings.append(cb1)
        readings.append(cb2)
        readings.append(cb3)

        return readings, angle_car, car_move

    def get_move(self, encoder):
        distance = encoder / 74.8
        return distance

    def go_straight(self, distance, x, y, angle):
        x_new = x + distance * np.cos(angle)
        y_new = y + distance * np.cos(angle)
        return x_new, y_new

    def go_around(self, alpha):
        new_angle = alpha
        return new_angle


# if __name__ == "__main__":
#     game_state = GameState()
#     while True:
#     #for i in range(2000):
#         #game_state = GameState()
#         game_state.frame_step((random.randint(0, 2)))