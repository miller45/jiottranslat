
import mqttcom
import configparser
import math
import time
import syslog

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

def slog(msg):
    syslog.syslog(msg)
    print(msg)

while onon:
    try:
        while True:
            currtime = math.trunc(time.time() * 1000)  # time in microseconds
            if currtime - pollPeriod > ltime:
                delta = currtime - ltime
                ltime = currtime
                mqttClient.ping_time(delta)  # ping the client to do timebased events

            if lstateCounter != mqttClient.stateCounter:
                lstateCounter = mqttClient.stateCounter
            time.sleep(0.01)

    except BaseException as error:
        slog('An exception occurred') #: {}'.format(error))
        slog('{}: {}'.format(type(error).__name__, error))
        if type(error) == KeyboardInterrupt:
            exit(0)
        slog("restarting after 5 secs")
        time.sleep(5)
    except:
        slog("exception occurred restarting after 1 secs")
        time.sleep(1)
