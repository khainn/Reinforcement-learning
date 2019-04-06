import sys
import serial
import time
import string
import math

import pymunk
from pymunk.vec2d import Vec2d



ser = serial.Serial('/dev/ttyUSB0', 9600)
# ser2 = serial.Serial('/dev/ttyUSB1', 9600)

# i = 0

def main():
    # global i
    # print('gui_tien')
    ser.write(b'2')
    # print('tien')
    readings = []
    read = []
    line = 0
    cb1 = 0
    cb2 = 0
    cb3 = 0
    flag_2 = 1
    angle_car = 0
    encoder = 0
    time.sleep(0.1)
    while flag_2:
        ser.reset_input_buffer()
        # print('gui_r')
        ser.write(b'r')
        # print('gui_r_ok')
        i = 0
        flag = 1
        t = 0
        # print('1')
        timetest = int(round(time.time()*1000))
        print(timetest)
        while flag:
            # print('0')
            for c in ser.read():
                t = t + 1
                readings.append(chr(c))
                if c == 36:
                    i = i + 1 
                if i == 6:
                    flag = 0
                print("t: %d  i:%d "%(t, i))
            timetest_1 = int(round(time.time()*1000))
            flag_2 = 0
            print(timetest_1)
            if (timetest_1 - timetest) > 350 : 
                # readings = ['$', '4', '0', '$', '4', '0', '$', '4', '0', '$', '1', '0', '1', '6', '$', '5', '.', '1', '8', '$']
                flag = 0
                flag_2 = 1
                print('flag')

        
    # print('r1')
    readings = ''.join(readings)
    # print('r2')
    line = readings.split('$')
    # print('l')
    cb1 = int(line[1])
    cb2 = int(line[2])
    cb3 = int(line[3])
    encoder = int(line[4])
    angle_car = float(line[5])

    read.append(cb1)
    read.append(cb2)
    read.append(cb3)

    orientate_goal = Vec2d(900 - cb1, 700 - cb2)
    orientate_car = Vec2d(1, 0).rotated(angle_car)
    orientation = orientate_car.get_angle() - orientate_goal.get_angle()

    distance = encoder / 74.8

    print(readings)
    print(distance)
    print(orientation)
    print(read)
    print('----------')

    time.sleep(0.4)
    ser.write(b's')
    # print('stop')
    time.sleep(0.5)

  
if __name__ == '__main__':
    while True:
        main()
        