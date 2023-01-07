"""
A small test code for the Sofar HYP 3-6 EP Inverter
Andre Wagner
https://www.facebook.com/groups/2477195449252168
Sofar Solar Inverter - Remote Control & Smart Home Integration
Version 2023.01.07
"""

import minimalmodbus
import serial
import struct

instrument = minimalmodbus.Instrument("/dev/ttyUSB1", 1, debug = True)  # port name, slave address
instrument.serial.baudrate = 9600  # Baud
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 0.5  # seconds
instrument.mode = minimalmodbus.MODE_RTU

instrument.clear_buffers_before_each_transaction = True

def manual(power = 0):
    # we need an active passiv mode, or this modul will crash and the hyd restart
    # set the passiv mode active
    instrument.write_register(4368, 3)
    # slpit the power to a byte
    values = struct.pack(">l", power)
    # split low and high byte
    low = struct.unpack(">H", bytearray([values[0], values[1]]))[0]
    high = struct.unpack(">H", bytearray([values[2], values[3]]))[0]
    # send the registers
    instrument.write_registers(4487, [0, 0, low, high, low, high])

def auto():
    # like a automatic mode
    instrument.write_register(4368, 0)

def standby():
    #just send a zweo power
    manual(0)
def read():
    # iḿ just an example
    hyd_solar_p = instrument.read_register(0x05C4) * 100
    print(f"Current Solar Power {hyd_solar_p} W")


read()
#auto()

#manual = pos: charge neg: discharge
#manual(1000)
standby()



