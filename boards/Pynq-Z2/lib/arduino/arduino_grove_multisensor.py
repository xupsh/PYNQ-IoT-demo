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
from . import LT_PINS
from . import ARDUINO_GROVE_G1
from . import ARDUINO_GROVE_G2
from . import ARDUINO_GROVE_G3
from . import ARDUINO_GROVE_G4
from . import ARDUINO_GROVE_G5
from . import ARDUINO_GROVE_G6
from . import ARDUINO_GROVE_G7



__author__ = "Cong Zou"
__copyright__ = "Copyright 2019, Xilinx"
__email__ = "pynq_support@xilinx.com"


ARDUINO_GROVE_MULTISENSOR_PROGRAM = "arduino_grove_multisensor.bin"
CONFIG_IOP_SWITCH = 0x1
GET_IMU_DATA =      0x3
GET_DTH_DATA =      0x5
GET_ALIGHT_DATA =   0x7


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


class Grove_multi(object):
    """This class controls the Grove IIC IMU, Grove light sensor V1.2
    and Grove GPIO DHT11. 
    
    Grove IMU 10DOF is a combination of grove IMU 9DOF (MPU9250) and grove 
    barometer sensor (BMP180). MPU-9250 is a 9-axis motion tracking device 
    that combines a 3-axis gyroscope, 3-axis accelerometer, 3-axis 
    magnetometer and a Digital Motion Processor (DMP). BMP180 is a high 
    precision, low power digital pressure sensor. Hardware version: v1.1.

    Grove DHT11 return temperature (Celcius) and humidity (percent)

    Grove light sensor can return both analog and digital signal, here we use
    only analog signal, 0-3.3V corresponding to 0-350 Lux
    
    Attributes
    ----------
    microblaze : Arduino
        Microblaze processor instance used by this module.
        
    """
    def __init__(self, mb_info, imu_pin = ARDUINO_GROVE_I2C, dth_pin = ARDUINO_GROVE_G2, al_pin = "CHANNEL_A0"):
        """Return a new instance of an Grove IMU object. 
        
        Parameters
        ----------
        mb_info : dict
            A dictionary storing Microblaze information, such as the
            IP name and the reset name.
        gr_pin: list
            A group of pins on arduino-grove shield.

        """
        if imu_pin not in [ARDUINO_GROVE_I2C]:
            raise ValueError("IMU pins can only be I2C.")

        if dth_pin not in [ARDUINO_GROVE_G1,
                          ARDUINO_GROVE_G2,
                          ARDUINO_GROVE_G3,
                          ARDUINO_GROVE_G4,
                          ARDUINO_GROVE_G5,
                          ARDUINO_GROVE_G6,
                          ARDUINO_GROVE_G7]:
            raise ValueError("DTH11 pins can only be G1 - G7.")

        if al_pin not in LT_PINS.keys():
            raise ValueError("Light sensor pins can only be A1 - A4.")

        pin = []
        pin.append(dth_pin[0])
        pin.append(LT_PINS[al_pin])
        print(pin)

        self.microblaze = Arduino(mb_info, ARDUINO_GROVE_MULTISENSOR_PROGRAM)
        self.microblaze.write_mailbox(0, pin)
        self.microblaze.write_blocking_command(CONFIG_IOP_SWITCH)

    def get_imu_data(self):
        """Get the whole data from the grove IMU.
        
        Returns
        -------
        list
            [0,1,2] A list of the acceleration data along X-axis, Y-axis, and Z-axis.
            [3,4,5] A list of the gyro data along X-axis, Y-axis, and Z-axis.
            [6,7,8] A list of the compass data along X-axis, Y-axis, and Z-axis.
            [9,10]  A list of the value of temperature and pressure.
        """
        self.microblaze.write_blocking_command(GET_IMU_DATA)
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
    def get_dht_data(self):
        """Get the whole data from the grove DTH11.
        
        Returns
        -------
        list
            [0,1] A list of data, [0] is temperature (Celcius), [1] is humidity (percent).
        """
        self.microblaze.write_blocking_command(GET_DTH_DATA)
        data = self.microblaze.read_mailbox(0, 2)
        [temp, humi] = [_reg2float(i) for i in data]

        return[float("{0:.2f}".format(temp)),
               float("{0:.2f}".format(humi))]

    def get_al_data(self):
        self.microblaze.write_blocking_command(GET_ALIGHT_DATA)
        voltage = self.microblaze.read_mailbox(0)
        voltage = _reg2float(voltage)

        return float("{0:.2f}".format((voltage*350) / 3.3))
        
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
        
        a = pres / 101325
        b = 1 / 5.255
        c = 1 - pow(a, b)
        altitude = 44300 * c
        return float("{0:.2f}".format(altitude))
