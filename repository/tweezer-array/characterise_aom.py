from artiq.experiment import *
from artiq.experiment import EnvExperiment
from artiq.gateware.eem import Phaser

import numpy as np


class CharacteriseOptics(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("camera_hardware")
        self.setattr_device("slm_cam")

        self.phaser0: Phaser = self.get_device("phaser0")

    @rpc
    def prepare(self) -> TList(TTuple([TFloat, TFloat])):

        # generate numpy array from -11.0 to 11.0 in 4 steps
        x_freqs = np.linspace(-11.0, 11.0, 7)
        y_freqs = np.linspace(-11.0, 11.0, 7)

        scan_coordinates = []
        for x in x_freqs:
            for y in y_freqs:
                scan_coordinates.append((x, y))

        return scan_coordinates

    @rpc
    def get_camera_hardware_image(self) -> TArray(TInt32, 2):

        image = self.camera_hardware.get_image()

        if image is None:
            raise ValueError("Camera hardware image is None")

        image = image.T

        self.set_dataset("camera_hardware_image", image, broadcast=True)

        print(f"Max pixel value in camera_hardware image: {np.max(image)}")

        return image

    @host_only
    def set_camera_exposure(self, exposure):
        self.camera_hardware.set_exposure(exposure)

    @rpc
    def auto_set_exposure(self):

        exposure = 4e-5 # this is minimum exposure time for the camera, in seconds

        self.set_camera_exposure(exposure)
        image = self.get_camera_hardware_image()
        max_pixel_value = np.max(image)

        goal_max_pixel_value = 800

        if max_pixel_value > 1021:
            raise ValueError(f"At minimum exposure time the camera saturated")

        exposure = exposure * goal_max_pixel_value / max_pixel_value

        self.set_camera_exposure(exposure)

        max_pixel_value = np.max(self.get_camera_hardware_image())

        print(f"Auto set camera exposure to {exposure}s, max pixel value = {max_pixel_value}")


    @rpc
    def get_everything_ready(self):
        #self.camera_hardware.set_woi((555, 140, 590, 180))
        self.slm_cam.create_new_characterisation_file()

    @rpc
    def save_characterisation_image(self, x, y):
        self.slm_cam.save_characterisation_image(x, y)

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

        self.phaser0.channel[0].oscillator[0].set_frequency(0.0)
        self.phaser0.channel[1].oscillator[0].set_frequency(0.0)

        self.auto_set_exposure()
        self.get_camera_hardware_image()

        print("Initialised Phaser")

        self.get_everything_ready()

        print("Initialised Camera")

        ###

        scan_coordinates = self.prepare()
        self.core.break_realtime()

        
        for x, y in scan_coordinates:
            self.phaser0.channel[0].oscillator[0].set_frequency(x*MHz)
            self.phaser0.channel[1].oscillator[0].set_frequency(y*MHz)

            self.save_characterisation_image(100+x, 100+y)

            self.core.break_realtime()
        