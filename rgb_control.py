import sys
import time
import traceback

import numpy as np
from bleak import BleakScanner, BleakClient
import platform

from bleak.exc import BleakDeviceNotFoundError, BleakDBusError


CLIENT = None
UU = None

async def get_client_and_uu():
    global CLIENT
    global UU
    
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
    return CLIENT, UU

# ELK-BLEDOM
if platform.system().lower() == 'macos':
    address = "380704A4-1064-E4CA-1F73-6B0C11F68AD0"
else:
    address = "BE:96:80:00:05:79"

async def power_on():
    client, uu = await get_client_and_uu()
    if not (client and uu):
        return
    value = bytes([0x7e, 0x00, 0x04, 0xf0, 0x00, 0x01, 0xff, 0x00, 0xef])
    await client.write_gatt_char(uu, value, response=False)

async def power_off():
    client, uu = await get_client_and_uu()
    if not (client and uu):
        return
    value = bytes([0x7e, 0x00, 0x04, 0x00, 0x00, 0x00, 0xff, 0x00, 0xef])
    await client.write_gatt_char(uu, value, response=False)


async def set_color(color):
    client, uu = await get_client_and_uu()
    if not (client and uu):
        return
    await power_on(client, uu)
    value = bytes([0x7e, 0x00, 0x05, 0x03, color[0], color[1], color[2], 0x00, 0xef])
    await client.write_gatt_char(uu, value, response=False)


async def set_brightness(value):
    client, uu = await get_client_and_uu()
    if not (client and uu):
        return
    await power_on(client, uu)
    value = bytes([0x7e, 0x00, 0x01, value, 0x00, 0x00, 0x00, 0x00, 0xef])
    await client.write_gatt_char(UU, value, response=False)


async def blink(color):
    client, uu = await get_client_and_uu()
    if not (client and uu):
        return
    await set_color(color, client, uu)
    time.sleep(1)
    for _ in range(3):
        for i in range(0, 64, 2):
            await set_brightness(i, client, uu)
        for i in range(64, 0, -2):
            await set_brightness(i,  client, uu)


async def connect():
    global CLIENT
    global UU
    if CLIENT:
        if CLIENT.is_connected:
            print('[RGB] Already connected')
            return
        else:
            print('[RGB] Disconnect')
            CLIENT = None
            UU = None
            
    print('[RGB] INIT CONNECTING...')
    scanner = BleakScanner()

    try:
        addresses = await scanner.discover(timeout=10)
    except BleakDBusError:
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
        time.sleep(5)
    except Exception as e:
        print(f'Error: {e}')
        traceback.print_exc(file=sys.stdout)

