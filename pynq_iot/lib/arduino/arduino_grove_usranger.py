#   Copyright (c) 2019, Xilinx, Inc.
#   All rights reserved.
# 
#   Redistribution and use in source and binary forms, with or without 
#   modification, are permitted provided that the following conditions are met:
#
#   1.  Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#
#   2.  Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the 
#       documentation and/or other materials provided with the distribution.
#
#   3.  Neither the name of the copyright holder nor the names of its 
#       contributors may be used to endorse or promote products derived from 
#       this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION). HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from pynq import Clocks
from . import Arduino
from . import ARDUINO_GROVE_G1
from . import ARDUINO_GROVE_G2
from . import ARDUINO_GROVE_G3
from . import ARDUINO_GROVE_G4
from . import ARDUINO_GROVE_G5
from . import ARDUINO_GROVE_G6
from . import ARDUINO_GROVE_G7

__author__ = "zou cong"
__copyright__ = "Copyright 2019, Xilinx"


ARDUINO_GROVE_USRANGER_PROGRAM = "arduino_grove_usranger.bin"

CONFIG_IOP_SWITCH = 0x1
GET_DISTANCE =      0x3

class Grove_usranger(object):
    """This class controls the grove_usranger. 
    
    Hardware version: v2.2.
    
    Attributes
    ----------
    microblaze : Arduino
        Microblaze processor instance used by this module.
        
    """
    def __init__(self, mb_info, gr_pin = ARDUINO_GROVE_G1):
        """Return a new instance of an Grove LEDbar object. 
        
        Parameters
        ----------
        mb_info : dict
            A dictionary storing Microblaze information, such as the
            IP name and the reset name.
        instruction: list
           instruction to controll the car

        """
        if gr_pin not in [ARDUINO_GROVE_G1,
                          ARDUINO_GROVE_G2,
                          ARDUINO_GROVE_G3,
                          ARDUINO_GROVE_G4,
                          ARDUINO_GROVE_G5,
                          ARDUINO_GROVE_G6,
                          ARDUINO_GROVE_G7]:
            raise ValueError("Group number can only be G1 - G7.")
        
        self.microblaze = Arduino(mb_info, ARDUINO_GROVE_USRANGER_PROGRAM)
        self.microblaze.write_mailbox(0, gr_pin)
        self.microblaze.write_blocking_command(CONFIG_IOP_SWITCH)

    def get_distance(self):
        '''
        get the distance from usranger
        
        Parameters
        ----------
        int : distance

        Returns
        -------
        None
        '''
        self.microblaze.write_blocking_command(GET_DISTANCE)
        raw_value = self.microblaze.read_mailbox(0)
        clk_period_ns = int(1000 / Clocks.fclk0_mhz)
        num_microseconds = raw_value * clk_period_ns * 0.001
        if num_microseconds * 0.001 > 30:
            return 500
        else:
            return num_microseconds/58
