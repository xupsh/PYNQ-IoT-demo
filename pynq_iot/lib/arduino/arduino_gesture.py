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
from . import GESTURE_DICT

__author__ = "zou cong"
__copyright__ = "Copyright 2019, Xilinx"

ARDUINO_GESTURE_PROGRAM = "arduino_gesture.bin"

CONFIG_IOP_SWITCH = 0x1
READ_GESTURE = 0X3

'''
Gesture sensor is fixed in A18,A19(i2c)

'''


class Gesture_sen(object):
    """This class controls the gesture sensor. 
    Hardware version: v2.2.
    
    Attributes
    ----------
    microblaze : Arduino
        Microblaze processor instance used by this module.
        
    """
    def __init__(self, mb_info):
        """Return a new instance of an gesture sensor object. 
        
        Parameters
        ----------
        mb_info : dict
            A dictionary storing Microblaze information, such as the
            IP name and the reset name.

        """
        self.microblaze = Arduino(mb_info,ARDUINO_GESTURE_PROGRAM)
        self.microblaze.write_blocking_command(CONFIG_IOP_SWITCH)
        data = self.microblaze.read_mailbox(0, 2)
        
        if not data[0]:
            raise ValueError("chip initialization failed.")
        
        if not data[1]:
            raise ValueError("gesture sensor initialization failed.")
        print("gesture sensor intialization succeed")
        
    def read_gesture(self):
        """Get the data from the geture sensor.
        
        Returns
        -------
        list
            A list of the data read from gesture sensor.
        
        """
        self.microblaze.write_blocking_command(READ_GESTURE)
        data = self.microblaze.read_mailbox(0, 2)
        if data[0]:
            if data[1] in GESTURE_DICT.keys():
                return GESTURE_DICT[data[1]]
            
        
        
