from artiq.experiment import *
import time


class IdleKernel(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("led1")

    @rpc
    def rpc1(self):
        print("hello world")


    @kernel
    def run(self):
        self.core.reset()

        for i in range(10):
            delay(5.0*s)

            # Schedule LED ON at now_mu()
            self.led1.on()
            self.core.break_realtime()
    
            # Wait until that RTIO timestamp actually occurs
            self.core.wait_until_mu(now_mu())

            # RPC executes while LED is physically ON
            self.rpc1()

            self.core.wait_until_mu(now_mu())

            # Keep LED on for another 500 ms
            delay(500*ms)
            self.led1.off()

            


            