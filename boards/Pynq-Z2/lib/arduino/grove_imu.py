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


import math
from . import Arduino
from . import ARDUINO_GROVE_I2C


__author__ = "Yun Rock Qu"
__developer__= "Cong Zou #made some change"
__copyright__ = "Copyright 2019, Xilinx"
__email__ = "pynq_support@xilinx.com"


ARDUINO_GROVE_IMU_PROGRAM = "grove_imu.bin"
CONFIG_IOP_SWITCH = 0x1
GET_DATA = 0x3


def _reg2float(reg):
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


def _reg2int(reg):
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


class G_IMU(object):
    """This class controls the Grove IIC IMU. 
    
    Grove IMU 10DOF is a combination of grove IMU 9DOF (MPU9250) and grove 
    barometer sensor (BMP180). MPU-9250 is a 9-axis motion tracking device 
    that combines a 3-axis gyroscope, 3-axis accelerometer, 3-axis 
    magnetometer and a Digital Motion Processor (DMP). BMP180 is a high 
    precision, low power digital pressure sensor. Hardware version: v1.1.
    
    Attributes
    ----------
    microblaze : Arduino
        Microblaze processor instance used by this module.
        
    """
    def __init__(self, mb_info, gr_pin):
        """Return a new instance of an Grove IMU object. 
        
        Parameters
        ----------
        mb_info : dict
            A dictionary storing Microblaze information, such as the
            IP name and the reset name.
        gr_pin: list
            A group of pins on arduino-grove shield.

        """
        if gr_pin not in [ARDUINO_GROVE_I2C]:
            raise ValueError("Group number can only be I2C.")

        self.microblaze = Arduino(mb_info, ARDUINO_GROVE_IMU_PROGRAM)
        self.microblaze.write_blocking_command(CONFIG_IOP_SWITCH)

    def get_data(self):
        """Get the whole data from the accelerometer.
        
        Returns
        -------
        list
            [0,1,2] A list of the acceleration data along X-axis, Y-axis, and Z-axis.
            [3,4,5] A list of the gyro data along X-axis, Y-axis, and Z-axis.
            [6,7,8] A list of the compass data along X-axis, Y-axis, and Z-axis.
            [9,10]  A list of the value of temperature and pressure.
        """
        self.microblaze.write_blocking_command(GET_DATA)
        data = self.microblaze.read_mailbox(0, 11)
        [ax, ay, az,
         gx, gy, gz,
         mx, my, mz,
         temp, pres] = [_reg2float(i) for i in data]

        return [float("{0:.2f}".format(ax / 16384)),
                float("{0:.2f}".format(ay / 16384)),
                float("{0:.2f}".format(az / 16384)),
                float("{0:.2f}".format(gx * 250 / 32768)),
                float("{0:.2f}".format(gy * 250 / 32768)),
                float("{0:.2f}".format(gz * 250 / 32768)),
                float("{0:.2f}".format(mx * 1200 / 4096)),
                float("{0:.2f}".format(my * 1200 / 4096)),
                float("{0:.2f}".format(mz * 1200 / 4096)),
                float("{0:.2f}".format(temp)),
                float("{0:.2f}".format(pres))]
        
    def get_heading(self):
        """Get the value of the heading.
        
        Returns
        -------
        float
            The angle deviated from the X-axis, toward the positive Y-axis.
        
        """
        [ax, ay, az,
         gx, gy, gz,
         mx, my, mz,
         temp, pres] = self.get_data()
        
        heading = 180 * math.atan2(my, mx) / math.pi
        if heading < 0:
            heading += 360
        return float("{0:.2f}".format(heading))

    def get_tilt_heading(self):
        """Get the value of the tilt heading.
        
        Returns
        -------
        float
            The tilt heading value.
        
        """
        [ax, ay, az,
         gx, gy, gz,
         mx, my, mz,
         temp, pres] = self.get_data()

        try:
            pitch = math.asin(-ax)
            roll = math.asin(ay / math.cos(pitch))
        except ZeroDivisionError:
            raise RuntimeError("Value out of range or device not connected.")

        xh = mx * math.cos(pitch) + mz * math.sin(pitch)
        yh = mx * math.sin(roll) * math.sin(pitch) + \
            my * math.cos(roll) - mz * math.sin(roll) * math.cos(pitch)
        _ = -mx * math.cos(roll) * math.sin(pitch) + \
            my * math.sin(roll) + mz * math.cos(roll) * math.cos(pitch)
        tilt_heading = 180 * math.atan2(yh, xh) / math.pi
        if yh < 0:
            tilt_heading += 360
        return float("{0:.2f}".format(tilt_heading))
        
        
    def get_atm(self):
        """Get the current pressure in relative atmosphere.

        Returns
        -------
        float
            The related atmosphere.
        
        """
        [ax, ay, az,
         gx, gy, gz,
         mx, my, mz,
         temp, pres] = self.get_data()
        
        return float("{0:.2f}".format(pres / 101325))
        
    def get_altitude(self):
        """Get the current altitude.
        
        Returns
        -------
        float
            The altitude value.
        
        """
        [ax, ay, az,
         gx, gy, gz,
         mx, my, mz,
         temp, pres] = self.get_data()
        
        a = pres / 1000
        b = 1 / 5.25885
        c = 288.15 - math.exp((math.log(a) + 18.2573)*b)
        altitude = (1/0.0065) * c
        return float("{0:.2f}".format(altitude))
