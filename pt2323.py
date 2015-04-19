#!/usr/bin/python

import smbus
import time

bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

DEVICE_ADDRESS = 74      #7 bit address (will be left shifted to add the read write bit)
DEVICE_REG_MODE1 = 0x00
DEVICE_REG_LEDOUT0 = 0x1d

#Write a single register
print("PT2323_IN6CH")
bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0xC7)
time.sleep(2.0)
print("PT2323_INST1")
bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0xCB)
time.sleep(2.0) 
print("PT2323_INST2")
#bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0xCA)
#time.sleep(2.0)
print("PT2323_INST3")
#bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0xC9)
#time.sleep(2.0)
print("PT2323_INST4")
#bus.write_byte_data(DEVICE_ADDRESS, DEVICE_REG_MODE1, 0xC8)
#time.sleep(2.0)
