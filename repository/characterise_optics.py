from artiq.experiment import *
from artiq.experiment import EnvExperiment
from artiq.gateware.eem import Phaser

import numpy as np


class CharacteriseOptics(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("camera")
        self.phaser0: Phaser = self.get_device("phaser0")

    def prepare(self) -> TList(TTuple([TFloat, TFloat])):

        # generate numpy array from -10.0 to 10.0 in steps of 1.0
        x_freqs = np.arange(-10.0, 11.0, 2.0)
        y_freqs = np.arange(-10.0, 11.0, 2.0)

        scan_coordinates = []
        for x in x_freqs:
            for y in y_freqs:
                scan_coordinates.append((x, y))

        return scan_coordinates

    @kernel
    def run(self):

        self.core.reset()
        self.core.break_realtime()
        self.phaser0.init()
        self.core.break_realtime()

        duc = 100*MHz
        
        self.phaser0.channel[0].set_duc_frequency(duc)
        self.phaser0.channel[0].set_duc_cfg()
        self.phaser0.channel[0].set_att(0*dB)

        self.phaser0.channel[1].set_duc_frequency(duc)
        self.phaser0.channel[1].set_duc_cfg()
        self.phaser0.channel[1].set_att(0*dB)

        self.phaser0.duc_stb()

        self.core.break_realtime()

        self.phaser0.channel[0].oscillator[0].set_amplitude_phase(1.0)
        self.phaser0.channel[1].oscillator[0].set_amplitude_phase(1.0)

        print("Initialised Phaser")

        self.camera.initialise_camera()
        self.camera.create_new_characterisation_file()
        self.camera.set_exposure(0.002)
        self.camera.set_gain(0)
        self.camera.set_roi(483, 1323, 114, 958)

        print("Initialised Camera")

        ###

        scan_coordinates = self.prepare()
        self.core.break_realtime()

        
        for x, y in scan_coordinates:
            self.phaser0.channel[0].oscillator[0].set_frequency(x*MHz)
            self.phaser0.channel[1].oscillator[0].set_frequency(y*MHz)

            self.camera.take_photo(100+x, 100+y)

            self.core.break_realtime()


        ###

        print("Closing Camera")
        
        self.camera.close_camera()
        