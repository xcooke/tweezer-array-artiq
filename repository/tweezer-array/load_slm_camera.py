import pickle

from artiq.experiment import *
from artiq.experiment import EnvExperiment
from artiq.gateware.eem import Phaser
from artiq.language.core import delay, at_mu, now_mu
from artiq.language.units import dB, MHz, ms, s
from artiq.coredevice.core import Core
from artiq.coredevice.phaser import Phaser



import numpy as np

import time



class LoadCameras(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.core: Core
        self.setattr_device("camera_hardware")
        self.setattr_device("slm")
        self.setattr_device("slm_cam")
        self.setattr_device("camera_tweezers")
        self.setattr_device("camera_fluorescence")
        self.setattr_device("atoms")

        self.phaser0: Phaser = self.get_device("phaser0")


    @rpc
    def get_camera_hardware_image(self) -> TArray(TInt32, 2):

        image = self.camera_hardware.get_image()

        if image is None:
            raise ValueError("Camera hardware image is None")

        image = image.T

        #image[30, 20] = 500

        # pixel values are of type uint16
        # for the kernel to handle them properly, we need to convert them to int32 when output
        # but the dataset and applet can store uint16

        self.set_dataset("camera_hardware_image", image, broadcast=True)

        # find maximum value in image and print it
        #print("Max pixel value in camera_hardware image: ", np.max(image))

        print(f"Max pixel value in camera_hardware image: {np.max(image)}")

        return image

    @rpc
    def get_fluorescence_image(self) -> TArray(TInt32, 2):

        self.camera_fluorescence.set_woi()

        image = self.camera_fluorescence.get_image()

        if image is None:
            raise ValueError("Camera fluorescence image is None")

        image = image.T

        # pixel values are of type uint16
        # for the kernel to handle them properly, we need to convert them to int32 when output
        # but the dataset and applet can store uint16

        self.set_dataset("camera_fluorescence_image", image, broadcast=True)

        # find maximum value in image and print it
        print("Max pixel value in camera_fluorescence image: ", np.max(image))

        return image

    @host_only
    def set_camera_exposure(self, exposure):
        self.camera_hardware.set_exposure(exposure)

    @rpc
    def set_slm_phase(self):
        self.slm_cam.set_phase()

    @host_only
    def clear_slm_phase(self):
        self.slm_cam.clear_phase()

    @host_only
    def load_atoms(self, threshold=600):
        self.atoms.load_atoms(threshold)

    @host_only
    def set_camera_woi(self):
        self.camera_hardware.set_woi((555, 140, 590, 180))
        # for some reason I can't make this smaller
        #self.camera_hardware.set_woi(None)
        # (0, 0) is top right
        # so (x, y) is coordinate measured from top right of image
        # (x, width, y, height)

    @host_only
    def load_aom_calibration(self):
        
        filename = "/home/stronlab/artiq/position_calibration.pkl"

        with open(filename, "rb") as f:
            self.aom_calibration = pickle.load(f)

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
    def fourier_calibrate(self):

        self.slm_cam.fourier_calibrate()


    @rpc
    def get_everything_ready(self):
        #self.set_camera_woi()
        self.load_aom_calibration()
        self.set_slm_phase()
        self.auto_set_exposure()
        #self.set_camera_exposure(4e-3)
        #self.load_atoms(600)
        self.take_picture()
        #self.take_picture()
        print("everything ready")
        """
        self.clear_slm_phase()
        self.auto_set_exposure()
        self.take_picture()
        """
        #self.find_aom_range()
        """
        #self.set_camera_exposure(8e-5)
        
        self.set_slm_phase()
        self.auto_set_exposure()
        self.load_atoms(600)
        self.get_camera_hardware_image()

        print("everything ready and loaded atoms")
        """

    @rpc
    def take_picture(self):
        self.get_camera_hardware_image()
        self.get_fluorescence_image()
        #time.sleep(1)

    @rpc
    def find_aom_spot_parameters(self, x, y, amp) -> TTuple([TFloat, TFloat, TFloat]):

        calibration = self.aom_calibration
        p = np.array([[x, y]], dtype=float)

        x_freq = float(calibration["x_freq_interp"](p)[0])
        y_freq = float(calibration["y_freq_interp"](p)[0])

        local_amp = float(
            calibration["amplitude_interp"](p)[0]
        )

        amplitude_modification = (
            calibration["reference_amplitude"]
            / local_amp
        )

        amplitude_out = np.sqrt(amp * amplitude_modification)

        print("find_aom_spot_parameters: x_freq = {}, y_freq = {}, amplitude_out = {}".format(
            x_freq, y_freq, amplitude_out
        ))

        if x_freq is np.nan:
            return 0.0, 0.0, 1.0

        return x_freq-100, y_freq-100, amplitude_out

    @rpc
    def get_tweezer_locations(self, threshold: int) -> TList(TTuple([TFloat, TFloat])):

        tweezer_locations = self.slm_cam.get_tweezer_locations(threshold=threshold)

        print(f"Found {len(tweezer_locations)} tweezer locations")

        """
        hardware_image = self.get_dataset("camera_hardware_image")

        # on each tweezer location modify hardware_image with a value of 1500 at that location
        for x, y in tweezer_locations:
            hardware_image[y, x] = 1500

        #self.set_dataset("camera_hardware_image", hardware_image, broadcast=True)
        """

        # sort tweezer_locations by x and then y coordinate

        tweezer_locations.sort(key=lambda loc: (loc[0], loc[1]))

        return tweezer_locations

    @rpc
    def get_theoretical_slm_tweezer_locations(self) -> TList(TTuple([TFloat, TFloat])):

        locations = self.slm_cam.get_theoretical_slm_tweezer_locations()

        return [(float(x), float(y)) for x, y in locations]

    
    @kernel
    def set_aom_spot(self, freq_x=0.0, freq_y=0.0, amp_x=1.0, amp_y=1.0):

        # ensure freq_x, freq_x are within -12 and +12
        if freq_x < -12.0 or freq_x > 12.0:
            raise ValueError("freq_x must be between -12 and +12")
        if freq_y < -12.0 or freq_y > 12.0:
            raise ValueError("freq_y must be between -12 and +12")

        # ensure amp_x, amp_y are within 0 and 1
        if amp_x < 0.0 or amp_x > 1.0:
            raise ValueError("amp_x must be between 0 and 1")
        if amp_y < 0.0 or amp_y > 1.0:
            raise ValueError("amp_y must be between 0 and 1")

        self.phaser0.channel[0].oscillator[0].set_frequency(freq_x*MHz)
        self.phaser0.channel[0].oscillator[0].set_amplitude_phase(amp_x)
        delay(1*ms)

        self.phaser0.channel[1].oscillator[0].set_frequency(freq_y*MHz)
        self.phaser0.channel[1].oscillator[0].set_amplitude_phase(amp_y)
        delay(1*ms)
    

    @rpc
    def process_aom_range_spot(self) -> TTuple([TFloat, TFloat]):
        self.auto_set_exposure()
        self.take_picture()
        aom_tweezer_locations = self.get_tweezer_locations(threshold=100)
        if len(aom_tweezer_locations) == 0:
            raise ValueError("No tweezer locations found in AOM range spot")
        elif len(aom_tweezer_locations) > 1:
            raise ValueError("More than one tweezer location found in AOM range spot")

        return aom_tweezer_locations[0]

    @rpc
    def generate_slm_phase_pattern(self, aom_range, n):

        print(aom_range)

        print(n)

        self.slm_cam.generate_slm_phase_pattern(aom_range, n)

    @rpc
    def generate_rearrange_movements(
        self
    ) -> TList(TTuple([TFloat, TFloat, TFloat, TFloat])):

        self.auto_set_exposure()

        moves, sites = self.slm_cam.generate_rearrange_movements()

        tweezer_moves = []

        for src, dst in moves:
            tweezer_src = sites[src]
            tweezer_dst = sites[dst]

            tweezer_moves.append((
                float(tweezer_src[0]),
                float(tweezer_src[1]),
                float(tweezer_dst[0]),
                float(tweezer_dst[1])
            ))

        print(tweezer_moves)
        return tweezer_moves


    @rpc
    def move_atom(self, src, dst):

        self.atoms.move_atom(src, dst)



    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        self.phaser0.init()
        self.core.break_realtime()

        duc = 100 # MHz
        
        self.phaser0.channel[0].set_duc_frequency(duc*MHz)
        self.phaser0.channel[0].set_duc_cfg()
        self.phaser0.channel[0].set_att(0*dB)

        self.phaser0.channel[1].set_duc_frequency(duc*MHz)
        self.phaser0.channel[1].set_duc_cfg()
        self.phaser0.channel[1].set_att(0*dB)

        self.phaser0.duc_stb()
        self.core.break_realtime()
        """
        self.phaser0.channel[0].oscillator[0].set_amplitude_phase(1.0)
        self.phaser0.channel[1].oscillator[0].set_amplitude_phase(1.0)
        self.phaser0.channel[0].oscillator[0].set_frequency(0.0)
        self.phaser0.channel[1].oscillator[0].set_frequency(0.0)
        """

        self.get_everything_ready()
        self.core.break_realtime()

        """
        #slm_tweezer_locations = self.get_tweezer_locations(threshold=100)
        slm_tweezer_locations = self.get_theoretical_slm_tweezer_locations()
        self.core.break_realtime()

        
        for tweezer_x, tweezer_y in slm_tweezer_locations:
            x_freq, y_freq, amp = self.find_aom_spot_parameters(tweezer_x, tweezer_y, 1.0)

            self.core.break_realtime()

            try:

                self.set_aom_spot(x_freq, y_freq, amp, amp)

                self.core.break_realtime()


                self.take_picture()
                self.core.break_realtime()

            except:
                continue
        """
        

        
        t = 2.0
        dt = 0.3
        num_steps = int(t/dt)

        tweezer_moves = self.generate_rearrange_movements()
        self.core.break_realtime()

        
        for move in tweezer_moves:
            src_x = move[0]
            src_y = move[1]
            dst_x = move[2]
            dst_y = move[3]

            src = (src_x, src_y)
            dst = (dst_x, dst_y)

            for step in range(num_steps):
                
                frac = (step + 1) / num_steps
                x = src_x + frac * (dst_x - src_x)
                y = src_y + frac * (dst_y - src_y)

                self.core.wait_until_mu(now_mu())
                freq_x, freq_y, amp = self.find_aom_spot_parameters(x, y, 1.0)
                self.core.wait_until_mu(now_mu())

                self.core.break_realtime()

                amp_x = amp
                amp_y = amp

                # ensure freq_x, freq_x are within -10 and +10
                if freq_x < -10.0 or freq_x > 10.0:
                    raise ValueError("freq_x must be between -10 and +10")
                if freq_y < -10.0 or freq_y > 10.0:
                    raise ValueError("freq_y must be between -10 and +10")
        
                # ensure amp_x, amp_y are within 0 and 1
                if amp_x < 0.0 or amp_x > 1.0:
                    raise ValueError("amp_x must be between 0 and 1")
                if amp_y < 0.0 or amp_y > 1.0:
                    raise ValueError("amp_y must be between 0 and 1")
        
                self.phaser0.channel[0].oscillator[0].set_frequency(freq_x*MHz)
                self.phaser0.channel[0].oscillator[0].set_amplitude_phase(amp_x)
                delay(1*ms)
        
                self.phaser0.channel[1].oscillator[0].set_frequency(freq_y*MHz)
                self.phaser0.channel[1].oscillator[0].set_amplitude_phase(amp_y)
                delay(1*ms)


                self.core.wait_until_mu(now_mu())
                self.take_picture()
                self.core.wait_until_mu(now_mu())

                self.core.break_realtime()

                delay(dt)

            self.core.wait_until_mu(now_mu())
            self.move_atom(src, dst)
            self.core.wait_until_mu(now_mu())

            self.core.wait_until_mu(now_mu())
            self.take_picture()
            self.core.wait_until_mu(now_mu())
        