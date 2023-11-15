import sys
import time
import traceback

import numpy as np
from bleak import BleakScanner, BleakClient
import platform

from bleak.exc import BleakDeviceNotFoundError


# ELK-BLEDOM
if platform.system().lower() == 'macos':
    address = "380704A4-1064-E4CA-1F73-6B0C11F68AD0"
else:
    address = "BE:96:80:00:05:79"

async def power_on(client, uu):
    value = bytes([0x7e, 0x00, 0x04, 0xf0, 0x00, 0x01, 0xff, 0x00, 0xef])
    await client.write_gatt_char(uu, value, response=False)

async def power_off(client, uu):
    value = bytes([0x7e, 0x00, 0x04, 0x00, 0x00, 0x00, 0xff, 0x00, 0xef])
    await client.write_gatt_char(uu, value, response=False)


async def set_color(color, client, uu):
    await power_on(client, uu)
    value = bytes([0x7e, 0x00, 0x05, 0x03, color[0], color[1], color[2], 0x00, 0xef])
    await client.write_gatt_char(uu, value, response=False)


async def set_brightness(value, client, uu):
    await power_on(client, uu)
    value = bytes([0x7e, 0x00, 0x01, value, 0x00, 0x00, 0x00, 0x00, 0xef])
    await client.write_gatt_char(uu, value, response=False)


async def blink(color, client, uu):
    await set_color(color, client, uu)
    time.sleep(1)
    for _ in range(3):
        for i in range(0, 64, 2):
            await set_brightness(i, client, uu)
        for i in range(64, 0, -2):
            await set_brightness(i, client, uu)


async def main():
    while True:
        print('[RGB] STARTING RGB CONTROL MODULE')
        scanner = BleakScanner()
        # try:
        print(f'[RGB] discovering...')
        addresses = await scanner.discover(timeout=10)
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
            continue
        try:
            async with BleakClient(address) as client:
                print('[RGB] Successful connection')
                s = client.services
                uu = s.get_characteristic(13)
                current_color = '#00ffff'
                current_brightness = 5
                await power_on(client, uu)

                while True:
                    if not client.is_connected:
                        break
                    try:
                        with open('color.txt', 'r') as f:
                            l = f.readline()
                            color, brightness = l.split()
                            if color == 'OFF':
                                await power_off(client, uu)
                                color = '-1'
                                brightness = '-1'

                            if color == 'ON':
                                await power_on(client, uu)
                                color = '-1'
                                brightness = '-1'


                            if color == '.' or color == '-1':
                                color = current_color

                            if brightness == '.' or brightness == '-1' :
                                brightness = current_brightness
                            else:
                                if brightness not in ['ON', 'OFF']:
                                    brightness = round(float(brightness))

                            # TODO: color and brightness in one function

                        if color not in [current_color, '#000000', 'ON', 'OFF']:
                            try:
                                current_color = color
                                value = color.replace('#', '')
                                color_s = value[0:2], value[2:4], value[4:]
                                print(f'Setting up color: {color} {color_s}')
                                r, g, b = [int(i, 16) for i in color_s]
                            except Exception as e:
                                print('[RGB] Error in setting color')
                                traceback.print_exc(file=sys.stdout)
                            await set_color((r, g, b), client, uu)
                        elif brightness not in [-100, current_brightness, 'ON', 'OFF']:
                            try:
                                current_brightness = brightness
                                value = round(float(brightness))
                                if value > 100:
                                    value = 100
                                if value < 0:
                                    value = 0
                                value = round(np.linspace(0, 64, 100)[value-1])

                                print(f'Setting up brightness: {value}')
                                await set_brightness(value, client, uu)
                            except Exception as e:
                                print('[RGB] Error in setting brightness')
                                traceback.print_exc(file=sys.stdout)
                    except Exception as e:
                        print(f'Error setting rgb: {e}')
                        traceback.print_exc(file=sys.stdout)
                        time.sleep(5)
                        continue
                    reset()
                    time.sleep(0.1)
        except BleakDeviceNotFoundError:
            print('Could not connect to RGB device. Retrying in 5 secs...')
            traceback.print_exc(file=sys.stdout)
            time.sleep(5)
        except Exception as e:
            print(f'Error: {e}')
            traceback.print_exc(file=sys.stdout)
            time.sleep(5)

def reset():
    with open('color.txt', 'w') as f:
        f.write(f'-1 -1')
        f.flush()
        f.close()


def write_rgb_color(color):
    with open('color.txt', 'w') as f:
        f.write(f'{color} -1')
        f.flush()
        f.close()

def write_brightness(brightness):
    print('SETUP BRIGHTNESS')
    with open('color.txt', 'w') as f:
        f.write(f'-1 {brightness}')
        f.flush()
        f.close()


def write_rgb_color_and_brightness(color, brightness):
    with open('color.txt', 'w') as f:
        f.write(f'{color} {brightness}')
        f.flush()
        f.close()


def write_power_off():
    with open('color.txt', 'w') as f:
        f.write(f'OFF OFF')
        f.flush()
        f.close()

def write_power_on():
    with open('color.txt', 'w') as f:
        f.write(f'ON ON')
        f.flush()
        f.close()

def brightness_up_smooth():
    for brightness in range(0, 100, 5):
        with open('color.txt', 'w') as f:
            f.write(f'-1 {brightness}')
            f.flush()
            f.close()
            time.sleep(1)

