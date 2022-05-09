import paho.mqtt.client as mqtt
import posixpath as path
import syslog


class Eintrag:
    nextEventTime = -1
    nextEventMsg = ""
    nextEventTgt = ""

    def __init__(self, event_time, event_msg, event_tgt):
        self.nextEventTime = event_time
        self.nextEventMsg = event_msg
        self.nextEventTgt = event_tgt


class MQTTComm:
    swState = {}
    stateCounter = 0
    timeMS = 0
    connected = False
    eintraege = []

    def __init__(self, server_address, real_topic, virtual_topic):
        self.server_address = server_address
        self.real_topic = real_topic
        self.virtual_topic = virtual_topic
        self.actuator_topic = path.join("cmnd", real_topic)
        self.roller_topic = path.join("cmnd", virtual_topic)
        self.result_topic = path.join("stat", virtual_topic)
        self.slog("roller topic: {}".format(self.roller_topic))

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
        self.slog("ping called")
        self.client.publish(path.join(self.roller_topic, "STATUS"), "Ping from jiottranslat v2.1")

    def ping_time(self, delta):
        self.timeMS = self.timeMS + delta
        todos = []
        for en in reversed(self.eintraege):
            if 0 < en.nextEventTime < self.timeMS:
                todos.append(en)
                self.eintraege.remove(en)
        if len(todos) > 0:
            for td in todos:
                (swiname, onoff) = td.nextEventMsg.split(":")
                self.send_to_real(td.nextEventTgt, swiname, onoff)
            self.slog("eintrage ueber {}".format(len(self.eintraege)))

    def on_connect(self, client, userdata, flags, rc):
        self.slog("Connect with result code " + str(rc))
        self.connected = True

    def on_message(self, client, userdata, msg):
        # (head, tail) = path.split(msg.topic)
        parts = path.split(msg.topic)
        item = parts[-1]
        payload = str(msg.payload)
        if payload and payload.startswith("BLINDS"):
            laststate = self.swState.get(item, "")
            if msg.payload == "BLINDSUP":
                self.swState[item] = "BLINDSUP"
                self.send_to_real(item, "POWER1", "ON")
                self.send_to_real(item, "POWER2", "OFF")
                self.slog("Getting Up")
            elif msg.payload == "BLINDSDOWN":
                self.swState[item] = "BLINDSDOWN"
                self.send_to_real(item, "POWER1", "OFF")
                self.send_to_real(item, "POWER2", "ON")
                self.slog("Getting DOWN")
            elif msg.payload == "BLINDSSTOP":
                self.slog("Getting STOP")
                if laststate == "BLINDSSTOP":
                    self.send_to_real(item, "POWER1", "ON")
                    self.send_to_real(item, "POWER2", "ON")
                    self.enqueue_next_event(self.timeMS + 100, "POWER1:OFF", item)
                    self.enqueue_next_event(self.timeMS + 100, "POWER2:OFF", item)
                    self.swState[item] = "BLINDSSTOP2"
                else:
                    self.swState[item] = "BLINDSSTOP"

        self.stateCounter = self.stateCounter + 1
        # if(msg.topic.ends)

        self.slog(msg.topic + " " + str(msg.payload))

    def enqueue_next_event(self, event_time, event_msg, event_tgt):
        entry = Eintrag(event_time, event_msg, event_tgt)
        self.eintraege.append(entry)

    def send_to_real(self, item_name, switch_name, value):
        self.client.publish(path.join(self.actuator_topic, item_name, switch_name), value)

    def slog(self, msg):
        syslog.syslog(msg)
        print(msg)
