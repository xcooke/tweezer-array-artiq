from artiq.experiment import *
from artiq.coredevice.phaser import Phaser


class PhasorNoDMA(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.phaser0: Phaser = self.get_device("phaser0")

    @kernel
    def run(self):
        self.core.reset()

        self.phaser0.init()
        delay(1*ms)

        duc = 100*MHz

        self.phaser0.channel[0].set_duc_frequency(duc)
        self.phaser0.channel[0].set_duc_cfg()
        self.phaser0.channel[0].set_att(0*dB)

        self.phaser0.channel[1].set_duc_frequency(duc)
        self.phaser0.channel[1].set_duc_cfg()
        self.phaser0.channel[1].set_att(0*dB)

        self.phaser0.duc_stb()

        self.core.break_realtime()

        self.phaser0.channel[0].oscillator[0].set_frequency(0.0*MHz)
        self.phaser0.channel[0].oscillator[0].set_amplitude_phase(1.0)
        delay(1*ms)

        self.phaser0.channel[1].oscillator[0].set_frequency(0.0*MHz)
        self.phaser0.channel[1].oscillator[0].set_amplitude_phase(1.0)
        delay(1*ms)

        t = 5

        dt = 900e-9

        pulses = int((t / dt)*0.5)

        self.core.break_realtime()

        for i in range(pulses):
            self.phaser0.channel[0].oscillator[0].set_frequency(-10.0*MHz)
            self.phaser0.channel[0].oscillator[0].set_amplitude_phase(1.0)
            delay(dt)

            self.phaser0.channel[0].oscillator[0].set_frequency(10.0*MHz)
            self.phaser0.channel[0].oscillator[0].set_amplitude_phase(1.0)
            delay(dt)