import mqttcom
import configparser
import math
import time
import syslog

print("Starting Rollershutter IO Translator")

hpConfig = configparser.ConfigParser()
hpConfig.read("config.ini")

preshutter_names = hpConfig["mqtt"]["shutter_names"].strip().split(",")
shutter_names = []

for sn in preshutter_names:
    shutter_names.append(sn.strip())

def slog(msg):
    syslog.syslog(msg)
    print(msg)


def connecit():
    doinit = True

    while doinit:
        try:
            mqttClient = mqttcom.MQTTComm(hpConfig["mqtt"]["server_address"], hpConfig["mqtt"]["real_topic"],
                                          hpConfig["mqtt"]["virtual_topic"], shutter_names)
            doinit = False
            mqttClient.ping()
            return mqttClient

        except BaseException as error:
            slog('An exception occurred during init')  #: {}'.format(error))
            slog('{}: {}'.format(type(error).__name__, error))
            if type(error) == KeyboardInterrupt:
                exit(0)
            slog("restarting after 5 secs")
            time.sleep(5)
    return None


mqttClient = connecit()
lctime = math.trunc(time.time() * 1000)
pollPeriod = 100
check_period = 5000

lstateCounter = 0
ltime = 0


spamltime = 0

onon = True

while onon:
    try:
        while True:
            currtime = math.trunc(time.time() * 1000)  # time in microseconds
            if currtime - pollPeriod > ltime:
                delta = currtime - ltime
                mqttClient.ping_time(delta)  # ping the client to do timebased events

                ltime = currtime
            if currtime - check_period > lctime:
                if not mqttClient.client.is_connected():
                    slog("not connected retrying")
                    mqttClient = connecit()
                else:
                    mqttClient.send_tele(currtime)
                lctime = currtime
            if lstateCounter != mqttClient.stateCounter:
                lstateCounter = mqttClient.stateCounter
            time.sleep(0.01)

    except BaseException as error:
        slog('An exception occurred during onon')  #: {}'.format(error))
        slog('{}: {}'.format(type(error).__name__, error))
        if type(error) == KeyboardInterrupt:
            exit(0)
        slog("restarting after 5 secs")
        time.sleep(5)
    except:
        slog("exception occurred restarting after 1 secs")
        time.sleep(1)
