from artiq.experiment import *
from artiq.language.core import delay
from artiq.language.units import dB, MHz, ms, s
from artiq.coredevice.phaser import Phaser
import numpy as np

class LaserCircler(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.phaser0: Phaser = self.get_device("phaser0")


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

        time = 1 # in seconds
        steps = 100 # number of steps in the circle

        # generate a list of steps of costheta from theta = 0 to theta = 2pi
        costheta_list = [np.cos(2*np.pi*i/steps)*10 for i in range(steps)]

        # and a list of steps of sintheta from theta = 0 to theta = 2pi
        sintheta_list = [np.sin(2*np.pi*i/steps)*10 for i in range(steps)]

        # calculate time step so circle takes 1 second
        time_step = time/steps

        print(time_step)
        
        self.core.break_realtime()

        while True:
            for i in range(steps):
                x_adj_freq_MHz = costheta_list[i] * MHz
                y_adj_freq_MHz = sintheta_list[i] * MHz

                self.phaser0.channel[0].oscillator[0].set_frequency(x_adj_freq_MHz)
                self.phaser0.channel[0].oscillator[0].set_amplitude_phase(0.5)

                self.phaser0.channel[1].oscillator[0].set_frequency(y_adj_freq_MHz)
                self.phaser0.channel[1].oscillator[0].set_amplitude_phase(0.5)

                delay(time_step)
        