import random
import math
import numpy as np

import pymunk
from pymunk.vec2d import Vec2d

import string

import sys
import serial
import time

timetest = int(time.time()*1000)
print()

ser = serial.Serial('/dev/ttyUSB0', 9600)

goal_x = 1000
goal_y = 700
car_x = 50
car_y = 30

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
            print(angle_car)
            angle_car = self.go_around(angle_car)
            print('trai')
            print(angle_car)
        elif action == 1:   #phai
            ser.write(b'1')
            time.sleep(0.5)
            readings, angle_car, car_move = self.get_sonar_readings()
            print(angle_car)
            angle_car = self.go_around(angle_car)
            print('phai')
            print(angle_car)
        elif action == 2:   #thang
            ser.write(b'2')  
            time.sleep(0.5)
            readings, angle_car, car_move = self.get_sonar_readings()
            print(angle_car)
            car_x, car_y = self.go_straight(car_move, car_x, car_y, angle_car)
            print('thang')


        distance = np.sqrt((car_x - goal_x)**2 + (car_y - goal_y)**2)
        orientate_goal = Vec2d(goal_x - car_x, goal_y - car_y)
        orientate_car = Vec2d(1, 0).rotated(angle_car)
        orientation = orientate_car.get_angle() - orientate_goal.get_angle()
        print(orientate_car.get_angle())
        print(orientate_goal.get_angle())
        normalized_readings = [(x-20.0)/20.0 for x in readings]
        normalized_readings.append(orientation)
        normalized_readings.append(-orientation)
        # normalized_readings.append(distance)
        state = np.array([normalized_readings])
        print('distance: %d orientation: %f angleCar: %f'%(distance, orientation, angle_car))

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
            ser.write(b's')
            time.sleep(20)
            # goal_x = 1000 - goal_x
            # goal_y = 700 - goal_y
            # reward = 500
#            reward = self.last_steps - self.num_steps # reward for reaching the objective faster than last round (may want to scale this)
            self.last_steps = self.num_steps 
            self.num_steps = 0

        self.num_steps += 1
        # last_distance = distance
        # time.sleep(0.5)

        return reward, state, distance

    def car_is_crashed(self, readings):
        if readings[0] <= 8 or readings[1] <= 8 or readings[2] <= 8:
            return True
        else:
            return False

    def recover_from_crash(self):
        while self.crashed:
            self.crashed = False
            # ser.write(b's')
            # time.sleep(0.1)
            print('crash')
            ser.write(b'b')
            time.sleep(0.5)
            ser.write(b'1')
            time.sleep(0.5)
            
   
    def sum_readings(self, readings):
        """Sum the number of non-zero readings."""
        tot = 0
        for i in readings:
            tot += i
        return tot

    def get_sonar_readings(self):
        read_uart = []
        read_str = []
        readings = []
        read_cb = 0
        cb1 = 0
        cb2 = 0
        cb3 = 0
        angle_car = 0
        encoder = 0
        car_move = 0
        flag_2 = 1

        while flag_2:
            ser.reset_input_buffer()
            ser.write(b'r')
        
            i = 0
            flag = 1
            timetest = int(round(time.time()*1000))

            while flag:
                for c in ser.read():
                    if c == 36:
                        i = i + 1 
                read_uart.append(chr(c))
                if i == 6:
                    flag = 0
                timetest_1 = int(round(time.time()*1000))
                flag_2 = 0
            if (timetest_1 - timetest) > 350 : 
                print('flag')
                flag = 0
                flag_2 = 1
            print('read dont')
        read_str = ''.join(read_uart)
        read_cb = read_str.split('$')

        cb1 = read_cb[1]
        cb2 = read_cb[2]
        cb3 = read_cb[3]
        encoder = read_cb[4]
        angle_car = float(read_cb[5])

        car_move = self.get_move(int(encoder))

        readings.append(int(cb1))
        readings.append(int(cb2))
        readings.append(int(cb3))
        print(read_str)
        return readings, angle_car, car_move
        time.sleep(0.02)

    def get_move(self, encoder):
        distance = encoder / 74.8
        return distance

    def go_straight(self, distance, x, y, angle):
        angle = angle - 3.14
        x_new = x + distance * math.cos(angle)
        y_new = y + distance * math.cos(angle)
        return x_new, y_new

    def go_around(self, alpha):
        new_angle = alpha - 3.14
        return new_angle


# if __name__ == "__main__":
#     game_state = GameState()
#     while True:
#     #for i in range(2000):
#         #game_state = GameState()
#         game_state.frame_step((random.randint(0, 2)))