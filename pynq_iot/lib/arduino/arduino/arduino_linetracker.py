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

from . import Arduino
from . import LT_PINS

__author__ = "zou cong"
__copyright__ = "Copyright 2019, Xilinx"

ARDUINO_LINERTRACKER_PROGRAM = "arduino_linetracker.bin"

CONFIG_IOP_SWITCH = 0x1
READ_LT_DATA = 0X3

'''
There are two linetrackers
left 0, right 1
should be connected into A0-A5
LT_PINS = {"CHANNEL_A0":0,"CHANNEL_A1":1,"CHANNEL_A2":2,
           "CHANNEL_A3":3,"CHANNEL_A4":4,"CHANNEL_A5":5
    }

'''

def reg2float(reg):
    """Converts 32-bit register value to floats in Python.

    Parameters
    ----------
    reg: int
        A 32-bit register value read from the mailbox.

    Returns
    -------
    float
        A float number translated from the register value.

    """
    if reg == 0:
        return 0.0
    sign = (reg & 0x80000000) >> 31 & 0x01
    exp = ((reg & 0x7f800000) >> 23) - 127
    if exp == 0:
        man = (reg & 0x007fffff) / pow(2, 23)
    else:
        man = 1 + (reg & 0x007fffff) / pow(2, 23)
    result = pow(2, exp) * man * ((sign * -2) + 1)
    return float("{0:.2f}".format(result))


def reg2int(reg):
    """Converts 32-bit register value to signed integer in Python.

    Parameters
    ----------
    reg: int
        A 32-bit register value read from the mailbox.

    Returns
    -------
    int
        A signed integer translated from the register value.

    """
    result = -(reg >> 31 & 0x1) * (1 << 31)
    for i in range(31):
        result += (reg >> i & 0x1) * (1 << i)
    return result


class LT_sen(object):
    """This class controls the linetracker sensor. 
    Hardware version: v2.2.
    
    Attributes
    ----------
    microblaze : Arduino
        Microblaze processor instance used by this module.
        
    """
    def __init__(self, mb_info, left_pin = "CHANNEL_A3", right_pin = "CHANNEL_A2"):
        """Return a new instance of an Grove IMU object. 
        
        Parameters
        ----------
        mb_info : dict
            A dictionary storing Microblaze information, such as the
            IP name and the reset name.
        left_pin, right_pin : int

        """
        if right_pin not in LT_PINS.keys():
            raise ValueError("right linetracker should be set in the A0-A5.")
        
        if left_pin not in LT_PINS.keys():
            raise ValueError("left linetracker should be set in the A0-A5.")
        data_in = []
        data_in.append(LT_PINS[left_pin])
        data_in.append(LT_PINS[right_pin])

        self.microblaze = Arduino(mb_info,ARDUINO_LINERTRACKER_PROGRAM)
        self.microblaze.write_mailbox(0, data_in)
        self.microblaze.write_blocking_command(CONFIG_IOP_SWITCH)
        
    def read_lt_data(self):
        """Get the data from the accelerometer.
        
        Returns
        -------
        list
            A list of the data read from linetracker sensor.
        
        """
        self.microblaze.write_blocking_command(READ_LT_DATA)
        data = self.microblaze.read_mailbox(0, 4)
        digital_left = reg2int(data[0])
        digital_right = reg2int(data[1])
        analog_left = reg2float(data[2])
        analog_right = reg2float(data[3])
        return data
        
    
