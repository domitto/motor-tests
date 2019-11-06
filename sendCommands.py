from pylibftdi import Device
import struct
import serial
from time import sleep
import datetime

def reg_addr(ch, offset):
    if ch == 1:
        return 0x11831000 + offset
    elif ch == 2:
        return 0x11832000 + offset
    elif ch == 3:
        return 0x11833000 + offset
    else:
        raise ValueError('not a valid channel')

def wav_addr(ch):
    if ch == 1:
        return 0xC0000000
    elif ch == 2:
        return 0x00054000
    elif ch == 3:
        return 0xC00A8000
    else:
        raise ValueError('not a valid channel')

def read_array(command,words):
    dev.write(struct.pack('<BIIB',0xA4,command,words,0x55))
    return struct.unpack('<BI%dBB' %(words*4),dev.read(words*4+6))

def read_single(command):
    dev.write(struct.pack('<BIB',0xA0,command,0x55))
    return struct.unpack('<BIiB',dev.read(10))[2]

def write_single(command,value):
    dev.write(struct.pack('<BIiB',0xA2,command,value,0x55))

def firmware_version():
    print("FW VERSION = \n")
    ver = read_array(0x11830028,5)
    print([hex(i) for i in ver])
    print("".join([chr(i) for i in ver[2:-1]]))

def load_waveform(dir,motor):
    if dir == 'p':
        print('loading positive array..\n')
        with open('npoint-axisdata/npoint-axis'+str(motor-1)+'-pos-waveform.log','r') as fp:
            line = fp.readline()
            while line:
                write_single(wav_addr(motor),line)
                sleep(0.01)
                line = fp.readline()
    elif dir == 'n':
        print('loading negative array..\n')
        with open('npoint-axisdata/npoint-axis'+str(motor-1)+'-neg-waveform.log','r') as fp:
            line = fp.readline()
            while line:
                write_single(wav_addr(motor),line)
                sleep(0.01)
                line = fp.readline()

def load_commands(motor):
    with open('npoint-axisdata/npoint-axis'+str(motor-1)+'.log') as fp:
        line = fp.readline()
        while line:
            addr = line.split()[2].split(',')[0]
            val = line.split()[4]
            print('press any key to write ',val, 'to addr ', addr)
            a = input('').split(" ")[0]
            write_single(addr,val)
            line = fp.readline()

def read_control_loop(ch):
        return read_single(reg_addr(ch,0x084))

def write_control_loop(ch,value):
        write_single(reg_addr(ch,0x084),value)

def control_loop(motor):
    print('(r) read current status')
    print('(c) change current status')
    a = input('').split(" ")[0]
    if(a == 'r'):
        print(read_control_loop(motor))
    elif(a == 'c'):
        print('enter new value [0-1]: ')
        val = int(input())
        if val == 0 or val == 1:
            write_control_loop(motor,val)

motor=1
with Device(mode='t') as dev:
    dev.baudrate = 115200
    a = ''
    motor = 1
    while(a != 'q'):
        print('Active Motor = ',motor)
        print('(m) change motor selection')
        print('(p) print firmware version')
        print('(l) control loop status')
        print('(w) load waveform file')
        print('(m) load commands file')
        print('(q) quit program')
        print('Enter command:')
        a = input('').split(" ")[0]
        if(a == 'm'):
            print("type motor number [1-3]: ")
            motor = int(input())
            if motor not in range(1,4):
                print('not a valid number, setting to motor 1..\n')
                motor = 1
        elif(a == 'p'):
            firmware_version()
        elif(a == 'l'):
            control_loop(motor)
        elif(a == 'w'):
            print('type direction: ')
            print('(p) positive')
            print('(n) negative')
            dir = input('').split(" ")[0]
            if dir == 'p' or dir == 'n':
                load_waveform(dir,motor)
        else(a == 'm'):
            load_commands(motor)
