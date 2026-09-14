from artiq.experiment import *
from artiq.language.core import delay
from artiq.language.units import dB, MHz, ms, s
from artiq.coredevice.phaser import Phaser

class LaserMover2D(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.phaser0: Phaser = self.get_device("phaser0")

        self.setattr_argument(
            "x_adj_freq", NumberValue(default=0, precision=0, step=1, type="int")
        )
        #self.x_adj_freq: int
        #self.x_adj_freq = 0

        self.setattr_argument(
            "y_adj_freq", NumberValue(default=0, precision=0, step=1, type="int")
        )
        #self.y_adj_freq: int
        #self.y_adj_freq = 0



    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()
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
        delay(1*ms)

        ## X

        # convert self.X_adj_freq and self.Y_adj_freq to MHz
        x_adj_freq_MHz = self.x_adj_freq * MHz
        y_adj_freq_MHz = self.y_adj_freq * MHz

        self.phaser0.channel[0].oscillator[0].set_frequency(x_adj_freq_MHz)
        self.phaser0.channel[0].oscillator[0].set_amplitude_phase(1.0)
        delay(1*ms)

        ## Y
        
        self.phaser0.channel[1].oscillator[0].set_frequency(y_adj_freq_MHz)
        self.phaser0.channel[1].oscillator[0].set_amplitude_phase(1.0)
        delay(1*ms)

        delay(1*s)
