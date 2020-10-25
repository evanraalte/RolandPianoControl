from RPi import GPIO
from time import sleep


class RotaryEncoder:

    def cb_rotation(self,channel):
        a_d0 = GPIO.input(self.pin_a)
        b_d0 = GPIO.input(self.pin_b)
        if b_d0 != a_d0:
            self.cb_r(self.piano,self.num,True)
        else:
            self.cb_r(self.piano,self.num,False)

    def cb_switch(self,channel):
        self.cb_sw(self.num)

    def __init__(self,pin_sw,pin_a,pin_b,num,cb_sw,cb_r,piano):
        self.cb_sw = cb_sw
        self.cb_r = cb_r
        self.num = num
        self.pin_a  = pin_a
        self.pin_b  = pin_b
        self.pin_sw = pin_sw
        self.piano = piano
        GPIO.setup(pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(pin_a, GPIO.BOTH, callback=self.cb_rotation, bouncetime=5)
        GPIO.add_event_detect(pin_sw, GPIO.RISING, callback=self.cb_switch, bouncetime=5)
    




