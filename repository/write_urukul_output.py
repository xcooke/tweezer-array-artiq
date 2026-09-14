import logging

from artiq.coredevice.ad9910 import AD9910
from artiq.coredevice.core import Core
from artiq.experiment import BooleanValue
from artiq.experiment import EnvExperiment
from artiq.experiment import NumberValue
from artiq.experiment import delay
from artiq.experiment import kernel

logger = logging.getLogger(__name__)


class WriteUrukulOutput(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.core: Core

        # I've labelled this as an AD9910, but it might be an AD9912 depending
        # on which training crate you are using. Some functions only exist on
        # the AD9910 class, but I won't call any of those ones here, so it will
        # still work. Notice how this type annotation doesn't actually affect
        # the functionality of the experiment: it's just a (useful) hint to
        # your editor so that you get helpful autocompletion while writing
        # code.
        self.dds: AD9910 = self.get_device("urukul0_ch0")

        self.setattr_argument("freq", NumberValue(default=10e6, unit="MHz"))
        self.setattr_argument("amp", NumberValue(default=1, max=1.0, min=0.0, precision=2)
        )
        self.setattr_argument("att", NumberValue(default=30.0, unit="dB"))
        self.setattr_argument("rf_sw", BooleanValue(default=True))

    @kernel
    def run(self):
        self.core.reset()
        self.dds.init(blind=False)

        logger.warning(
            "Setting attenuator to %.1f dB - this will affect all four channels",
            self.att,
        )

        logger.info(
            "%s - setting f=%.6f, att = %.1f dB, amp = %.2f, rf_sw=%s",
            "xanderlol",
            self.freq,
            self.att,
            self.amp,
            self.rf_sw,
        )

        self.core.break_realtime()
        delay(10e-3)

        self.dds.set(self.freq)
        self.dds.set_amplitude(self.amp)
        self.dds.set_att(self.att)
        self.dds.sw.set_o(self.rf_sw)
