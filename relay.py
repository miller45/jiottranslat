import RPi.GPIO as GPIO


class RelayBoard:
    Relay_Ch1 = 26
    Relay_Ch2 = 20
    Relay_Ch3 = 21

    def __init__(self):
        GPIO.setwarnings(True)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.Relay_Ch1,GPIO.OUT)
        GPIO.setup(self.Relay_Ch2,GPIO.OUT)
        GPIO.setup(self.Relay_Ch3,GPIO.OUT)
        GPIO.output(self.Relay_Ch1,GPIO.HIGH)
        GPIO.output(self.Relay_Ch2,GPIO.HIGH)
        GPIO.output(self.Relay_Ch3,GPIO.HIGH)
    
    def switchRelay1On(self):
        GPIO.output(self.Relay_Ch1,GPIO.LOW) # yes LOW means switching the relay on  weird but it is so
        print("switchRelay1On")

    def switchRelay1Off(self):
        GPIO.output(self.Relay_Ch1,GPIO.HIGH) # yes HIGH means switching the relay off  weird but it is so
        print("switchRelay1Off")

    def switchRelay2On(self):
        GPIO.output(self.Relay_Ch2, GPIO.LOW)
        print("switchRelay2On")
    def switchRelay2Off(self):
        GPIO.output(self.Relay_Ch2, GPIO.HIGH)
        print("switchRelay2Off")
    def switchRelay3On(self):
        GPIO.output(self.Relay_Ch3, GPIO.LOW)

    def switchRelay3Off(self):
        GPIO.output(self.Relay_Ch3, GPIO.HIGH)

    def cleanup(self):
        GPIO.cleanup()
        
        
        
