"""
A small test code for the Sofar HYP 3-6 EP Inverter
Andre Wagner
https://www.facebook.com/groups/2477195449252168
Sofar Solar Inverter - Remote Control & Smart Home Integration
Version 2023.12.31

A slightly increasing CRC counter is unfortunately normal depending on the HYD firmware.
"""



import minimalmodbus
import serial
import struct
import time

instrument = minimalmodbus.Instrument("/dev/ttyUSB1", 1, debug = False)  # port name, slave address
instrument.serial.baudrate = 9600  # Baud
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 0.5  # seconds
instrument.mode = minimalmodbus.MODE_RTU

instrument.clear_buffers_before_each_transaction = True

crc = 0  # counter for errors

# add all registers
value = {}
register = {
    'batterie_u': 0x0604,
    'batterie_i': 0x0605,
    'batterie_p': 0x0606,
    'batterie_temp': 0x0607,
    'batterie_soc': 0x0608,
    'batterie_cycle': 0x060a,
    'batterie_discharge_day': 0x0699,
    'batterie_charge_day': 0x0695,
    'grid_v': 0x048d,
    'grid_hz': 0x0484,
    'grid_i': 0x048d,
    'inverter_state': 0x0404,
    'inverter_heatsink_temp': 0x041a,
    'inverter_temp': 0x0418,
    'inverter_load_p': 0x04af,
    'inverter_system_p': 0x0485,
    'inverter_sell_grid': 0x0699,
    'inverter_buy_grid': 0x068d,
    'inverter_load_use': 0x0689,
    'solar_p': 0x05c4,
    'solar_pv1v': 0x0584,
    'solar_pv1i': 0x0585,
    'solar_pv1p': 0x0586,
    'solar_pv2v': 0x0587,
    'solar_pv2i': 0x0588,
    'solar_pv2p': 0x0589,
    'solar_p_day': 0x0685,
    'solar_p_total': 0x0687
}

# set all to 0
for x in register:
    value[x] = 0


def manual(power = 10):
    global crc
    try:
        current = 9  # override the "current" state
        # we need an active passiv mode first
        # read the current state
        current = instrument.read_register(4368)
        time.sleep(0.2)
        # if not 3 (passiv mode) set it to 3
        if current != 3:
            instrument.write_register(4368, 3)
            time.sleep(0.2)

        # prepare the power value
        values = struct.pack(">l", power)
        # split low and high byte
        low = struct.unpack(">H", bytearray([values[0], values[1]]))[0]
        high = struct.unpack(">H", bytearray([values[2], values[3]]))[0]

        # send the registers
        instrument.write_registers(4487, [0, 0, low, high, low, high])
        time.sleep(0.1)
    except:
        crc += 1


def auto():
    global crc
    try:
        current = instrument.read_register(4368)
        time.sleep(0.1)
        if current != 0:
            # if controlstatus is not 0 (auto) set it to 0
            instrument.write_register(4368, 0)
            time.sleep(0.1)

    except:
        crc += 1

def standby():
    # just send a zweo power
    # 0 = standby, 10 = stay online
    manual(0)
    

def read():
    global value, crc
    try:
        
        # read values
        for i in register:
            try:
                value[i] = instrument.read_register(register[i])
                time.sleep(0.1)
            except:
                crc += 1
                

        value["batterie_u"] /= 10
        value["grid_v"] /= 10
        value["grid_hz"] /= 100
        value["inverter_state"] += 10
        value["inverter_load_p"] *= 10
        value["inverter_system_p"] = move(value["inverter_system_p"]) * 10
        value["batterie_p"] = move(value["batterie_p"]) * 10
        value["batterie_i"] = move(value["batterie_i"]) / 100
    

        value["solar_pv1v"] /= 10
        value["solar_pv1i"] /= 100
        value["solar_pv1p"] *= 10
        value["solar_pv2v"] /= 10
        value["solar_pv2i"] /= 100
        value["solar_pv2p"] *= 10
        value["solar_p"] = value["solar_pv1p"] + value["solar_pv2p"]
        value["inverter_solar_p"] = value["solar_p"]
        value["solar_p_total"] /= 10
        value["solar_p_day"] /= 100
        value["batterie_ah"] = 0
        #gridw = loadw - systemw
        value["grid_p"] = value["inverter_load_p"] - value["inverter_system_p"]

        return value
    except:
        crc += 1


#functions to read negative values (like current eg)
def move(value):
    if value > 32767:
        value = 65535 - value
    return value






read()  # read all values (take some time)
print(value['batterie_soc'])

manual(-5000)

