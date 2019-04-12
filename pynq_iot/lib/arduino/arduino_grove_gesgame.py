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


ARDUINO_GROVE_GESGAME_PROGRAM = "arduino_grove_gesgame.bin"

CONFIG_IOP_SWITCH = 0x1
GET_GESTURE =       0x3
WRITE_LEDS =        0x5

GESTURE_MAP = {0: "no-detection",

               1: "forward",

               2: "backward",

               3: "right",

               4: "left",

               5: "up",

               6: "down",

               7: "clockwise",

               8: "counter-clockwise",

               9: "wave"

               }


class Grove_gesgame(object):
    """This class controls the gesture gameb based on arduino_grove. 
    
    Hardware version: v2.2.
    
    Attributes
    ----------
    microblaze : Arduino
        Microblaze processor instance used by this module.
        
    """
    def __init__(self, mb_info, led_pin = ARDUINO_GROVE_G4):
        """Return a new instance of an Grove LEDbar object. 
        
        Parameters
        ----------
        mb_info : dict
            A dictionary storing Microblaze information, such as the
            IP name and the reset name.
        pins: list
           pins connected to peripheral devices

        """
        if led_pin not in [ARDUINO_GROVE_G1,
                           ARDUINO_GROVE_G2,
                           ARDUINO_GROVE_G3,
                           ARDUINO_GROVE_G4,
                           ARDUINO_GROVE_G5,
                           ARDUINO_GROVE_G6,
                           ARDUINO_GROVE_G7]:
            raise ValueError("Group number of ledbar can only be G1 - G7.")
        
        self.microblaze = Arduino(mb_info, ARDUINO_GROVE_GESGAME_PROGRAM)
        self.microblaze.write_mailbox(0, led_pin)
        self.microblaze.write_blocking_command(CONFIG_IOP_SWITCH)

    def get_gesture(self):
        '''
        get the distance from usranger
        
        Parameters
        ----------
        int : distance

        Returns
        -------
        None
        '''
        self.microblaze.write_blocking_command(GET_GESTURE)
        value = self.microblaze.read_mailbox(0)
        return value
    
    def write_binary(self, data_in):
        """Set individual LEDs in the LEDbar based on 10 bit binary input.

        Each bit in the 10-bit `data_in` points to a LED position on the
        LEDbar. Red LED corresponds to the LSB, while green LED corresponds
        to the MSB.

        Parameters
        ----------
        data_in : int
            10 LSBs of this parameter control the LEDbar.

        Returns
        -------
        None

        """
        self.microblaze.write_mailbox(0, data_in)
        self.microblaze.write_blocking_command(WRITE_LEDS)
