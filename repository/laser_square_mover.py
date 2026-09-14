from artiq.experiment import *
from artiq.language.core import delay
from artiq.language.units import dB, MHz, ms, s
from artiq.coredevice.phaser import Phaser

class LaserSquareMover(EnvExperiment):
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

        time = 10 # in seconds
        steps = 100 # total number of steps in the square path
        side_span = 11.5 # frequency offset at each edge (+/- side_span MHz)
        side_steps = steps // 4

        # calculate time step so one full square takes 1 second
        time_step = time/steps

        print(time_step)
        
        self.core.break_realtime()

        while True:
            for i in range(steps):
                edge = i // side_steps
                edge_step = i % side_steps
                t = edge_step / side_steps

                if edge == 0:
                    x_adj_freq_MHz = (-side_span + 2.0*side_span*t) * MHz
                    y_adj_freq_MHz = (-side_span) * MHz
                elif edge == 1:
                    x_adj_freq_MHz = side_span * MHz
                    y_adj_freq_MHz = (-side_span + 2.0*side_span*t) * MHz
                elif edge == 2:
                    x_adj_freq_MHz = (side_span - 2.0*side_span*t) * MHz
                    y_adj_freq_MHz = side_span * MHz
                else:
                    x_adj_freq_MHz = (-side_span) * MHz
                    y_adj_freq_MHz = (side_span - 2.0*side_span*t) * MHz

                self.phaser0.channel[0].oscillator[0].set_frequency(x_adj_freq_MHz)
                self.phaser0.channel[0].oscillator[0].set_amplitude_phase(0.5)

                self.phaser0.channel[1].oscillator[0].set_frequency(y_adj_freq_MHz)
                self.phaser0.channel[1].oscillator[0].set_amplitude_phase(0.5)

                delay(time_step)
        