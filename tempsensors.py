import re,os
import time
class TempSensors:
    disableSensor1 = False
    disableSensor2 = False
    disableSensor3 = False
    disableSensor4 = False
    def __init__(self, w1name1, w1name2, wlname3, wlname4):
        self.sensor1path = "/sys/bus/w1/devices/" + w1name1 + "/w1_slave"
        self.sensor2path = "/sys/bus/w1/devices/" + w1name2 + "/w1_slave"
        self.sensor3path = "/sys/bus/w1/devices/" + wlname3 + "/w1_slave"
        self.sensor4path = "/sys/bus/w1/devices/" + wlname4 + "/w1_slave"

    def read_temperature1(self):
        ret = "-99"
        if self.disableSensor1:
            return ret
        try: 
            ret = self.read_sensor(self.sensor1path)
        except:
            self.disableSensor1 = True
        return ret
    def read_temperature2(self):
        ret = "-99"
        if self.disableSensor2:
            return ret
        try: 
            ret = self.read_sensor(self.sensor2path)
        except:
            self.disableSensor2 = True
        return ret

    def read_temperature3(self):
        ret = "-99"
        if self.disableSensor3:
            return ret
        try:
            ret = self.read_sensor(self.sensor3path)
        except:
            self.disableSensor3 = True
        return ret

    def read_temperature4(self):
        ret = "-99"
        if self.disableSensor4:
            return ret
        try:
            ret = self.read_sensor(self.sensor4path)
        except:
            self.disableSensor4 = True
        return ret

    def read_sensor(self,path):
        value = "U"
        try:
            f = open(path, "r")
            line = f.readline()
            if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):
                line = f.readline()
                m = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
                if m:
                    value = str(float(m.group(2)) / 1000.0)
            f.close()
        except IOError as e:
            print ("Error reading", path, ": ", e)
        return value
