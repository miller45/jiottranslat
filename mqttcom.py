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
    last_dir = {}  # last direction of shutters
    stateCounter = 0
    timeMS = 0
    connected = False
    eintraege = []
    use_stopped = True # use the stopped state

    def __init__(self, server_address, real_topic, virtual_topic, shutter_names):
        self.server_address = server_address
        self.real_topic = real_topic
        self.virtual_topic = virtual_topic
        self.actuator_topic = path.join("cmnd", real_topic)
        self.roller_topic = path.join("cmnd", virtual_topic)
        self.result_topic = path.join("stat", virtual_topic)
        self.tele_topic = path.join("tele", virtual_topic)
        self.tele_availtopic = path.join("tele/sonoff")  # needed to pass throught availbility of real devices
        self.shutter_names = shutter_names
        self.slog("roller topic: {}".format(self.roller_topic))

        self.client = mqtt.Client()
        self.connect()

    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.will_set(path.join(self.tele_topic, "allshutters", "LWT"), payload="Offline", qos=0, retain=True)

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
        self.client.publish(path.join(self.tele_topic, "allshutters", "LWT"), payload="Online", qos=0, retain=True)
        self.slog("Connect with result code " + str(rc))
        self.connected = True
        for shutn in self.shutter_names:
            shtp = path.join(self.result_topic, shutn, "position")
            self.client.publish(shtp, payload="50", qos=0, retain=False)
            shop = path.join(self.result_topic, shutn, "operation")
            self.client.publish(shop, payload="open", qos=0, retain=False)

    def on_message(self, client, userdata, msg):
        # (head, tail) = path.split(msg.topic)
        parts = msg.topic.split("/")
        item = parts[-1]
        is_hass = False
        if item == "set":  # detect home assistant
            is_hass = True
            item = parts[-2]  # the name is before the set
        payload = str(msg.payload)

        # home assitant handling
        if is_hass:
            if payload:
                if payload == "OPEN":
                    self.swState[item] = "BLINDSUP"
                    self.send_to_real(item, "POWER1", "ON")
                    self.send_to_real(item, "POWER2", "OFF")
                    self.slog("home assissent open (UP)")
                    self.client.publish(path.join(self.result_topic, item, "operation"), payload="opening", qos=0,
                                        retain=False)
                    self.client.publish(path.join(self.result_topic, item, "position"), payload="33", qos=0,
                                        retain=False)
                elif payload == "CLOSE":
                    self.swState[item] = "BLINDSDOWN"
                    self.send_to_real(item, "POWER1", "OFF")
                    self.send_to_real(item, "POWER2", "ON")
                    self.slog("home assissant close (DOWN)")
                    self.client.publish(path.join(self.result_topic, item, "operation"), payload="closing", qos=0,
                                        retain=False)
                    self.client.publish(path.join(self.result_topic, item, "position"), payload="66", qos=0,
                                        retain=False)
                elif payload == "STOP":
                    self.slog("home assissant stop")
                    prev_state = "closed"
                    if item in self.swState:
                        prev_state = self.swState[item]
                    self.send_to_real(item, "POWER1", "ON")
                    self.send_to_real(item, "POWER2", "ON")
                    self.swState[item] = "BLINDSSTOP2"
                    self.enqueue_next_event(self.timeMS + 100, "POWER1:OFF", item)
                    self.enqueue_next_event(self.timeMS + 100, "POWER2:OFF", item)
                    finstate = "closed" if prev_state == "BLINDSDOWN" else "open"
                    # Last direction is hint to final state
                    self.client.publish(path.join(self.result_topic, item, "operation"), payload=finstate, qos=0,
                                        retain=False)
                    # that  is is only for keeping homeassistant happy.  We do not really no were the shutters are

        # openhab handling
        elif payload and payload.startswith("BLINDS"):
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

    def send_tele(self, stamp, connected):
        msg = "CONNECTED {}" if connected else "NOT CONNECTED {}"
        self.client.publish(path.join(self.tele_topic, 'STATE'), msg.format(stamp))

    def slog(self, msg):
        syslog.syslog(msg)
        print(msg)
