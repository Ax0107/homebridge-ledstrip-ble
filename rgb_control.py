import sys
import time
import traceback

import numpy as np
from bleak import BleakScanner, BleakClient
import platform

from bleak.exc import BleakDeviceNotFoundError, BleakDBusError


CLIENT = None
UU = None
CONNECTING = False
SCANNER = None
Attempts = 0

async def get_client_and_uu():
    global CLIENT
    global UU
    try:
        if CLIENT:
            if CLIENT.is_connected:
                print('[RGB] Already connected')
                return
            else:
                print('[RGB] Disconnect')
                CLIENT = None
                UU = None
        
        while CLIENT is None or UU is None:
            try:
                await connect()
            except BleakDBusError:
                print('Already in progress...')
    except:
        return

# ELK-BLEDOM
if platform.system().lower() == 'macos':
    address = "380704A4-1064-E4CA-1F73-6B0C11F68AD0"
else:
    address = "BE:96:80:00:05:79"

async def power_on():
    global CLIENT
    global UU
    await get_client_and_uu()
    if CLIENT is None or UU is None:
        return
    
    value = bytes([0x7e, 0x00, 0x04, 0xf0, 0x00, 0x01, 0xff, 0x00, 0xef])
    await CLIENT.write_gatt_char(UU, value, response=False)

async def power_off():
    global CLIENT
    global UU
    await get_client_and_uu()
    if CLIENT is None or UU is None:
        return
    
    value = bytes([0x7e, 0x00, 0x04, 0x00, 0x00, 0x00, 0xff, 0x00, 0xef])
    await CLIENT.write_gatt_char(UU, value, response=False)


async def set_color(r, g, b):
    global CLIENT
    global UU
    await get_client_and_uu()
    if CLIENT is None or UU is None:
        return
    
    #r, g, b = [int(i, 16) for i in (r, g, b)]
    await power_on()
    value = bytes([0x7e, 0x00, 0x05, 0x03, r, g, b, 0x00, 0xef])
    await CLIENT.write_gatt_char(UU, value, response=False)


async def set_brightness(value):
    global CLIENT
    global UU
    await get_client_and_uu()
    if CLIENT is None or UU is None:
        return
    
    await power_on()
    value = bytes([0x7e, 0x00, 0x01, value, 0x00, 0x00, 0x00, 0x00, 0xef])
    await CLIENT.write_gatt_char(UU, value, response=False)


async def connect():
    global CLIENT
    global UU
    global CONNECTING
    global SCANNER
    global Attempts
    if CONNECTING:
        print('[RGB] already started connect')
        Attempts += 1
        if Attempts == 10:
            CONNECTING = False
        else:
            return
    
    if CLIENT:
        if CLIENT.is_connected:
            print('[RGB] Already connected')
            return
        else:
            print('[RGB] Disconnected')
            CLIENT = None
            UU = None
            
    print('[RGB] INIT CONNECTING...')
    CONNECTING = True
    
    if SCANNER is None:
        SCANNER = BleakScanner()
        
    try:
        addresses = await SCANNER.discover(timeout=3)
    except BleakDBusError:
        traceback.print_exc(file=sys.stdout)
        CONNECTING = False
        return
    print(f'[RGB] discovering...')
    address = None
    for device in addresses:
        print(device.address, device.name)
        if device.name and 'ELK-BLEDOM' in device.name:
            print('[RGB] DISCOVERED RGB-TAPE ELK-BLEDOM')
            address = device.address
            break
    
    print(f'[RGB] Target address: {address}')
    if address is None:
        print('[RGB] No RGB-tape. Trying reconnect...')
    try:
        CLIENT = BleakClient(address)
        await CLIENT.connect()
        print('[RGB] SUCCESSFULL CONNECTION')
        s = CLIENT.services
        UU = s.get_characteristic(13)
    except BleakDeviceNotFoundError:
        print('Could not connect to RGB device. Retrying in 5 secs...')
        traceback.print_exc(file=sys.stdout)
    except Exception as e:
        print(f'Error: {e}')
        traceback.print_exc(file=sys.stdout)
    CONNECTING = False
    SCANNER = None
