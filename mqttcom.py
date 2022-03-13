import paho.mqtt.client as mqtt
import posixpath as path

class MQTTComm:
    swState = {}
    stateCounter = 0
    timeMS = 0
    nextEventTime = -1
    nextEventMsg = ""
    nextEventTgt = ""

    def __init__(self, server_address, real_topic, virtual_topic):
        self.server_address = server_address
        self.real_topic = real_topic
        self.virtual_topic = virtual_topic
        self.actuator_topic = path.join("cmnd", real_topic)
        self.roller_topic = path.join("cmnd", virtual_topic)
        self.result_topic = path.join("stat", virtual_topic)
        print(self.roller_topic)

        self.client = mqtt.Client()
        self.connect()

    def connect(self):

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.server_address, 1883, 60)
        self.client.loop_start()
        self.client.subscribe(
            path.join(self.roller_topic, '#')
        )  # the hash symbol means we get all message from sensors*

    def ping(self):
        print("ping from mqtt")
        self.client.publish(path.join(self.roller_topic, "STATUS"), "Ping from heatingpi")
    def pingTime(self, delta):
        self.timeMS = self.timeMS + delta
        if 0 < self.nextEventTime <= self.timeMS:
            # print("elasped {}".format(self.nextEventTime))
            self.nextEventTime = -1
            if self.nextEventMsg == 'POWER1-2:OFF' and self.nextEventTgt:
                self.nextEventMsg = ""
                self.sendToReal(self.nextEventTgt, "POWER1", "OFF")
                self.sendToReal(self.nextEventTgt, "POWER2", "OFF")




    def switchOnOff(self, which, what):
        if which in self.swState:
            if self.swState[which] != what:
                self.client.publish("cmnd/sonoff/" + which + "/POWER", what)
                self.swState[which]=what
                print("switching "+which+" "+what)
        else:
            self.client.publish("cmnd/sonoff/" + which + "/POWER", what)
            self.swState[which] = what
            print("switching " + which + " " + what)

    def on_connect(self, client, userdata, flags, rc):
        print("Connect with result code " + str(rc))

    def on_message(self, client, userdata, msg):
        # (head, tail) = path.split(msg.topic)
        parts = path.split(msg.topic)
        item = parts[-1]
        payload = str(msg.payload)
        if payload and payload.startswith("BLINDS"):
            laststate = self.swState.get(item, "")
            if msg.payload == "BLINDSUP":
                self.swState[item] = "BLINDSUP"
                self.sendToReal(item, "POWER1", "ON")
                self.sendToReal(item, "POWER2", "OFF")
                print("Getting Up")
            elif msg.payload == "BLINDSDOWN":
                self.swState[item] = "BLINDSDOWN"
                self.sendToReal(item, "POWER1", "OFF")
                self.sendToReal(item, "POWER2", "ON")
                print("Getting DOWN")
            elif msg.payload == "BLINDSSTOP":
                print("Getting STOP")
                if laststate == "BLINDSSTOP":
                    self.sendToReal(item, "POWER1", "ON")
                    self.sendToReal(item, "POWER2", "ON")
                    self.nextEventTgt = ""
                    self.nextEventTime = self.timeMS + 100
                    self.nextEventMsg = "POWER1-2:OFF"
                    self.nextEventTgt = item
                    self.swState[item] = "BLINDSSTOP2"
                else:
                    self.swState[item] = "BLINDSSTOP"

        self.stateCounter = self.stateCounter + 1
        # if(msg.topic.ends)

        print(msg.topic + " " + str(msg.payload))

    def sendState(self, itemName, value):
        self.client.publish(path.join(self.result_topic, itemName), value)


    def sendToReal(self, itemName,switchName, value):
        self.client.publish(path.join(self.actuator_topic, itemName, switchName), value)



