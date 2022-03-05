import tempsensors
import relay
import time
import mqttcom
import configparser
import math
import arduino
import time


print("Starting HeatingPI V0.2")

ard= arduino.Arduino('/dev/ttyACM0')

hpConfig = configparser.ConfigParser()
hpConfig.read("config.ini")

#myOled = oled.OLED()
#myOled.showSplashScreen()

# mySens = tempsensors.TempSensors("28-3c01f0964f8c", "28-3c01f0965e56")
mySens = tempsensors.TempSensors(
    hpConfig["sensors"]["T1"],
    hpConfig["sensors"]["T2"],
    hpConfig["sensors"]["T3"],
    hpConfig["sensors"]["T4"]
)
# mySens = tempsensors.TempSensors("28-0317607252ff", "28-051760bdebff")

relayBoard = relay.RelayBoard()

mqttClient = mqttcom.MQTTComm(hpConfig["mqtt"]["server_address"], hpConfig["mqtt"]["base_topic"])

mqttClient.ping()
pollPeriod = int(hpConfig["control"]['poll_period'])
MQTTSpamPeriod = int(hpConfig["mqtt"]['tele_period'])

rotate = 0
lstateCounter = 0
ltime = 0
spamltime = 0
t1 = -99
t2 = -99
t3 = -99
t4 = -99
t5 = -99

onon=True

while onon:
    try:
        while True:
            currtime = math.trunc(time.time() * 1000)  # time in microseconds
            if currtime - pollPeriod > ltime:
                ltime = currtime
                t1 = float(mySens.read_temperature1())
                t2 = float(mySens.read_temperature2())
                t3 = float(mySens.read_temperature3())
                t4 = float(mySens.read_temperature4())
                t5 = float(ard.readRuecklauf())

                #regeln
                hysteresis=6
                offteresis=3
                SV=t3
                SR=t5
                SS=t4
                if (SS + hysteresis) <SR:
                    mqttClient.switchOnOff("52","ON")
                elif (SS + offteresis) >= SR:
                    mqttClient.switchOnOff("52", "OFF")


                #myOled.showTemperatures(t1, t2)
            if currtime - MQTTSpamPeriod > spamltime:
                spamltime = currtime
                mqttClient.sendTemperature("T1", t1)
                mqttClient.sendTemperature("T2", t2)
                mqttClient.sendTemperature("T3", t3)
                mqttClient.sendTemperature("T4", t4)
                mqttClient.sendTemperature("T5", t5)

            if lstateCounter != mqttClient.stateCounter:
                lstateCounter = mqttClient.stateCounter
                if mqttClient.relay1State:
                    relayBoard.switchRelay1On()
                else:
                    relayBoard.switchRelay1Off()
                if mqttClient.relay2State:
                    relayBoard.switchRelay2On()
                else:
                    relayBoard.switchRelay2Off()
                if mqttClient.relay3State:
                    relayBoard.switchRelay3On()
                else:
                    relayBoard.switchRelay3Off()
    except BaseException as error:
        relayBoard.cleanup()
        print('An exception occurred: {}'.format(error))
        print("restarting after 5 secs")
        time.sleep(5)
    except:
        relayBoard.cleanup()
        print("exception occurred restarting after 1 secs")
        time.sleep(1)
