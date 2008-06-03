from peephole.util import virtual

class Button(object):
    def __init__(self, lcd, name, keysym):
        self.name = name
        self.lcd = lcd
        self.keysym = keysym
        self.pressed_cbs = []
        self.backlight_cbs = []

    def setBacklight(self, state):
        for cb in self.backlight_cbs:
            cb(state)

    def registerBacklightCallback(self, cb):
        self.backlight_cbs.append(cb)

    def registerPressedCallback(self, cb):
        self.pressed_cbs.append(cb)

    def pressed(self):
        for cb in self.pressed_cbs:
            cb()
        # for folks using the old API...
        self.lcd.fire_btn_cb(self.keysym)
