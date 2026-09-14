from artiq.experiment import *
from artiq.coredevice.phaser import Phaser

class PhaserTone(EnvExperiment):
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

        ## X
        
        

        self.phaser0.channel[0].oscillator[2].set_frequency(0.0*MHz)
        self.phaser0.channel[0].oscillator[2].set_amplitude_phase(1.0)
        delay(1*ms)

        """
        self.phaser0.channel[0].oscillator[0].set_frequency(-10.0*MHz)
        self.phaser0.channel[0].oscillator[0].set_amplitude_phase(0.1)
        delay(1*ms)

        self.phaser0.channel[0].oscillator[1].set_frequency(-5.0*MHz)
        self.phaser0.channel[0].oscillator[1].set_amplitude_phase(0.1)
        delay(1*ms)

        self.phaser0.channel[0].oscillator[3].set_frequency(5.0*MHz)
        self.phaser0.channel[0].oscillator[3].set_amplitude_phase(0.1)
        delay(1*ms)

        self.phaser0.channel[0].oscillator[4].set_frequency(10.0*MHz)
        self.phaser0.channel[0].oscillator[4].set_amplitude_phase(0.1)
        delay(1*ms)
        """

        


        ## Y
        
        self.phaser0.channel[1].oscillator[0].set_frequency(0.0*MHz)
        self.phaser0.channel[1].oscillator[0].set_amplitude_phase(1.0)
        delay(1*ms)

        """
        self.phaser0.channel[1].oscillator[1].set_frequency(-10.0*MHz)
        self.phaser0.channel[1].oscillator[1].set_amplitude_phase(0.0)
        delay(1*ms)

        self.phaser0.channel[1].oscillator[3].set_frequency(5.0*MHz)
        self.phaser0.channel[1].oscillator[3].set_amplitude_phase(0.0)
        delay(1*ms)

        self.phaser0.channel[1].oscillator[4].set_frequency(-5.0*MHz)
        self.phaser0.channel[1].oscillator[4].set_amplitude_phase(0.0)
        delay(1*ms)

        self.phaser0.channel[1].oscillator[2].set_frequency(0.0*MHz)
        self.phaser0.channel[1].oscillator[2].set_amplitude_phase(0.0)
        delay(1*ms)
        """
        