import peephole.drivers.button

class Button(peephole.drivers.button.Button):
    def __init__(self, picolcd, name, keysym, led_number):
        peephole.drivers.button.Button.__init__(self, picolcd, name, keysym)
        self.led_number = led_number

    def setBacklight(self, state):
        self.lcd.leds[self.led_number] = state
        self.lcd.updateLeds()
        peephole.drivers.button.Button.setBacklight(self, state)

