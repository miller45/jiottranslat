
import mqttcom
import configparser
import math
import time

print("Starting Rollershutter IO Translator")


hpConfig = configparser.ConfigParser()
hpConfig.read("config.ini")

mqttClient = mqttcom.MQTTComm(hpConfig["mqtt"]["server_address"], hpConfig["mqtt"]["real_topic"], hpConfig["mqtt"]["virtual_topic"])

mqttClient.ping()
pollPeriod = 100


lstateCounter = 0
ltime = 0
spamltime = 0

onon = True

while onon:
    try:
        while True:
            currtime = math.trunc(time.time() * 1000)  # time in microseconds
            if currtime - pollPeriod > ltime:
                ltime = currtime
                mqttClient.pingTime(pollPeriod)  # ping the client to do timebased events

            if lstateCounter != mqttClient.stateCounter:
                lstateCounter = mqttClient.stateCounter

    except BaseException as error:
        print('An exception occurred') #: {}'.format(error))
        print('{}: {}'.format(type(error).__name__, error))
        if type(error) == KeyboardInterrupt:
            exit(0)
        print("restarting after 5 secs")
        time.sleep(5)
    except:
        print("exception occurred restarting after 1 secs")
        time.sleep(1)
