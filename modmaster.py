#!/usr/bin/env python
# -*- coding: utf-8 -*-

HOST = "192.168.1.143"
PORT = 4223
UID = "DKn" # Change XYZ to the UID of your RS485 Bricklet

import struct
import requests
import time
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_rs485 import BrickletRS485

expected_request_id = None

# Callback function for Modbus master write single register response callback
def cb_response(request_id, exception_code, input_registers):

    #print("Request ID: " + str(request_id))
    #print("Exception Code: " + str(exception_code))
    #print("Input Registers:" +str(input_registers))

    def get_float(input_registers, position):
        v = (input_registers[position] << 16) + input_registers[position + 1]
        f = struct.unpack('f', v.to_bytes(4, byteorder='little'))[0]
        return f 

    p1_voltage = get_float(input_registers, 0)
    p2_voltage = get_float(input_registers, 2)
    p3_voltage = get_float(input_registers, 4)
    p1_current = get_float(input_registers, 6)
    p2_current = get_float(input_registers, 8)
    p3_current = get_float(input_registers, 10)
    p1_power = get_float(input_registers, 12)
    p2_power = get_float(input_registers, 14)
    p3_power = get_float(input_registers, 16)
    hz_all = get_float(input_registers, 70)
    import_kwh = get_float(input_registers, 72)
    
    payload = {
        'p1_voltage': p1_voltage,
        'p2_voltage': p2_voltage,
        'p3_voltage': p3_voltage,
        'p1_current': p1_current,
        'p2_current': p2_current,
        'p3_current': p3_current,
        'sum_current': p1_current + p2_current + p3_current,
        'p1_power': p1_power,
        'p2_power': p2_power,
        'p3_power': p3_power,
        'sum_power': p1_power + p2_power + p3_power,
        'hz_all': hz_all,
        'import_kwh': import_kwh,
        'import_kwh_total': import_kwh
    }
    
    print(payload)

    try:
        r = requests.post('https://api.datacake.co/integrations/api/f83cad90-1c9f-4c78-ae7d-c1201f12ffdf/', json=payload)
        print(r)
    except Exception as e:
        print(e)

    if request_id != expected_request_id:
        print("Error: Unexpected request ID")

if __name__ == "__main__":

    ipcon = IPConnection()
    rs485 = BrickletRS485(UID, ipcon)

    ipcon.connect(HOST, PORT)

    rs485.set_mode(rs485.MODE_MODBUS_MASTER_RTU)
    rs485.register_callback(rs485.CALLBACK_MODBUS_MASTER_READ_INPUT_REGISTERS_RESPONSE, cb_response)
    rs485.set_modbus_configuration(1, 2000)

    start_time = time.time()
    
    print("Requesting Data and forwarding to Datacake...")
    expected_request_id = rs485.modbus_master_read_input_registers(1, 1, 76)

    while True:

        elapsed_time = time.time() - start_time

        if (elapsed_time > 300):
            print("")
            print("Requesting Data and forwarding to Datacake...")
            start_time = time.time()
            expected_request_id = rs485.modbus_master_read_input_registers(1, 1, 76)

        time.sleep(1)

    input("Press key to exit\n") # Use raw_input() in Python 2
    ipcon.disconnect()