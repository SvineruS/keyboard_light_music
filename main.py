import soundcard as sc
import numpy
from os import system


HISTORY_LENGTH = 10

LIGHT_1 = 0.5
LIGHT_2 = 0.7
LIGHT_3 = 0.85


class Main:
    def __init__(self):
        self.history = LastAvg(HISTORY_LENGTH)
        self.mic = sc.all_microphones(True)[0]

        self.old_light_value = 0

        with self.mic.recorder(samplerate=48000, channels=1) as rec:
            while True:
                data = rec.record(numframes=2**10)
                self.calculate(data)

    def calculate(self, data):
        data = numpy.average(abs(data))
        self.history.add(data)

        val = data / self.history.max()
        val = val ** 1.5  # increase picks

        if val > LIGHT_3:
            self.change_led(3)
        elif val > LIGHT_2:
            self.change_led(2)
        elif val > LIGHT_1:
            self.change_led(1)
        else:
            self.change_led(0)

    def change_led(self, f):
        if self.old_light_value == f:
            return

        system(fr"echo {f} | sudo tee /sys/class/leds/asus::kbd_backlight/brightness")
        self.old_light_value = f


class LastAvg:
    values = []

    def __init__(self, size):
        self.size = size

    def add(self, other):
        self.values.append(other)
        while len(self.values) > self.size:
            del self.values[0]

    def max(self):
        return max(self.values) or 1

    def avg(self):
        return numpy.average(self.values) or 1


Main()
