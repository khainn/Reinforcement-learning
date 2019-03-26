import sys
import serial
import time
import string

ser = serial.Serial('/dev/ttyUSB3', 9600)
# ser2 = serial.Serial('/dev/ttyUSB1', 9600)

def main():
    
    # print(sys.version)            
    # print(serial.__version__)
    # ser.write(b'1')
    # time.sleep(1)
    # ser.write(b'0')
    # time.sleep(1)
    # t = ser.read(2)
    # if t == b'63':
    # t = ser.readline()
    # while (i < 4):
    #   line = ser.read()
    #   if line == '$':
    #       i = i + 1
    #   lines.append(line)
    # print(lines)
    # lines = line.
    # ser.write(b'2')
    # time.sleep(1)
    # ser.write(b'1')
    # time.sleep(1)
    # ser.write(b'0')
    # time.sleep(1)
    ser.write(b'2')
    ser.write(b'r')

    line = []
    cb1 = []
    cb2 = []
    cb3 = []
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
            if i == 4:
                flag = 0
            line.append(chr(c))
    
    cb1 = int((''.join(cb1)), 0)       
    cb2 = int((''.join(cb2)), 0)
    cb3 = int((''.join(cb3)), 0)
    # t = ''.join(line)

    print(cb1)
    print(cb2)
    print(cb3)
    print('----------')

    time.sleep(0.5)
    ser.write(b's')
    time.sleep(0.5)
    
       
    
    # t = str(line)

    # if t == "$25$62$1$":
    #    print('true')
    # else :
    #    print('false')



if __name__ == '__main__':
    while True:
        main()
        