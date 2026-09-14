import numpy as np

from artiq.experiment import *
from artiq.coredevice.phaser import Phaser
from artiq.language.core import delay
from artiq.language.units import dB, MHz, ms, s


class Rearrange(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.setattr_device("atoms")
        self.setattr_device("slm")
        self.setattr_device("slm_cam")
        self.phaser0: Phaser = self.get_device("phaser0")

    @kernel
    def record(self, dt, num_states, states, collision_delay=10e-9):

        # states has shape:
        # (num_steps, 10, 2)
        #
        # states[i, oscillator, 0] = frequency in MHz
        # states[i, oscillator, 1] = amplitude
        #
        # oscillators 0-4 -> Phaser channel 0
        # oscillators 5-9 -> Phaser channel 1

        with self.core_dma.record("pulses"):

            for i in range(num_states):
                self.phaser0.channel[0].oscillator[0].set_frequency(
                    states[i, 0, 0] * MHz
                )
                delay(collision_delay)
                self.phaser0.channel[0].oscillator[1].set_frequency(
                    states[i, 1, 0] * MHz
                )
                delay(collision_delay)
                self.phaser0.channel[0].oscillator[2].set_frequency(
                    states[i, 2, 0] * MHz
                )
                delay(collision_delay)
                self.phaser0.channel[0].oscillator[3].set_frequency(
                    states[i, 3, 0] * MHz
                )
                delay(collision_delay)
                self.phaser0.channel[0].oscillator[4].set_frequency(
                    states[i, 4, 0] * MHz
                )
                delay(collision_delay)
    
                self.phaser0.channel[1].oscillator[0].set_frequency(
                    states[i, 5, 0] * MHz
                )
                delay(collision_delay)
                self.phaser0.channel[1].oscillator[1].set_frequency(
                    states[i, 6, 0] * MHz
                )
                delay(collision_delay)
                self.phaser0.channel[1].oscillator[2].set_frequency(
                    states[i, 7, 0] * MHz
                )
                delay(collision_delay)
                self.phaser0.channel[1].oscillator[3].set_frequency(
                    states[i, 8, 0] * MHz
                )
                delay(collision_delay)
                self.phaser0.channel[1].oscillator[4].set_frequency(
                    states[i, 9, 0] * MHz
                )
                delay(collision_delay)
    
                self.phaser0.channel[0].oscillator[0].set_amplitude_phase(
                    amplitude=states[i, 0, 1]
                )
                delay(collision_delay)
                self.phaser0.channel[0].oscillator[1].set_amplitude_phase(
                    amplitude=states[i, 1, 1]
                )
                delay(collision_delay)
                self.phaser0.channel[0].oscillator[2].set_amplitude_phase(
                    amplitude=states[i, 2, 1]
                )
                delay(collision_delay)
                self.phaser0.channel[0].oscillator[3].set_amplitude_phase(
                    amplitude=states[i, 3, 1]
                )
                delay(collision_delay)
                self.phaser0.channel[0].oscillator[4].set_amplitude_phase(
                    amplitude=states[i, 4, 1]
                )
                delay(collision_delay)
    
                self.phaser0.channel[1].oscillator[0].set_amplitude_phase(
                    amplitude=states[i, 5, 1]
                )
                delay(collision_delay)
                self.phaser0.channel[1].oscillator[1].set_amplitude_phase(
                    amplitude=states[i, 6, 1]
                )
                delay(collision_delay)
                self.phaser0.channel[1].oscillator[2].set_amplitude_phase(
                    amplitude=states[i, 7, 1]
                )
                delay(collision_delay)
                self.phaser0.channel[1].oscillator[3].set_amplitude_phase(
                    amplitude=states[i, 8, 1]
                )
                delay(collision_delay)
                self.phaser0.channel[1].oscillator[4].set_amplitude_phase(
                    amplitude=states[i, 9, 1]
                )
                delay(collision_delay)
                delay(dt)


    @rpc
    def load_atoms(self, threshold=600, seed=42):
        self.atoms.load_atoms(threshold, seed)

    @rpc
    def set_slm_phase(self):
        self.slm_cam.set_phase()

    @rpc
    def generate_tweezer_states(self, num_states) -> TArray(TFloat, 3):
        states = np.zeros((num_states, 10, 2), dtype=np.float64)

        for index in range(num_states):
            states[index, 0, 0] = -10.0 + 20.0 * index / (num_states - 1)
            states[index, 0, 1] = 0.3

            states[index, 1, 0] = -5.0 + 10.0 * index / (num_states - 1)
            states[index, 1, 1] = 0.3

            states[index, 2, 0] = 0.0
            states[index, 2, 1] = 0.3

            states[index, 5, 0] = 0.0
            states[index, 5, 1] = 1.0

        return states
    
    @rpc
    def generate_tetris_rearrange_movements(self, T, dt) -> TTuple([TArray(TFloat, 3), TInt32]):

        states = self.slm_cam.generate_tetris_rearrange_movements(T, dt)

        num_states = states.shape[0]

        return states, num_states


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

        self.load_atoms(threshold=600, seed=2)
        self.core.break_realtime()

        self.set_slm_phase()
        self.core.break_realtime()

        collision_delay = 10e-9

        t = 1.0
        dt = 0.1 # smallest dt is 800ns because otherwise underflow (40 ns * 20 = 800 ns)
        #num_steps = int(t / dt)

        dt = dt - collision_delay * 20

        #states = self.generate_tweezer_states(num_steps)
        states, num_states = self.generate_tetris_rearrange_movements(t, dt)
        self.core.break_realtime()
        
        
        self.record(dt, num_states, states, collision_delay)
        pulses_handle = self.core_dma.get_handle("pulses")
        self.core.break_realtime()

        self.core_dma.playback_handle(pulses_handle)
        

        

        