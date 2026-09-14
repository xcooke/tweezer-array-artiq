from artiq.experiment import *
from artiq.coredevice.phaser import Phaser

class TestPhaserLED(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.phaser0: Phaser = self.get_device("phaser0")

    @kernel
    def run(self):
        self.core.reset()
        self.phaser0.set_leds(0x00)  # Turn on LED0
        #self.phaser0.set_leds(0x00)  # Turn off all LEDs ?