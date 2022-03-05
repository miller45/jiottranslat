#!/usr/bin/env python3
import serial
import re

class Arduino:
    def __init__(self, port):
        self.port=port
        self.last=-98
        self.ser = serial.Serial(port, 115200, timeout=1) #'/dev/ttyACM0'
        self.ser.reset_input_buffer()
    def readRuecklauf(self):
        while self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8').rstrip()
            if line.startswith("T"):
                temp=line[1:]
                if re.match(r"^[0-9.]+$", temp):
                    self.last=float(temp)
        return self.last



