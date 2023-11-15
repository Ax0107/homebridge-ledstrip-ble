# homebridge-ledstrip-ble

This plugin let you control RGB ledstrip of ELK-BLEDOM using homebridge and python
Control On/Off, Hue, Saturation and Brightness

## Prerequisite
You need to have a bluetooth device. Check using `hcitool dev` command. You may also need root access with Homebridge

To run without root access, go to homebridge terminal and type ```sudo setcap cap_net_raw+eip $(eval readlink -f `which node`)```

## Installation 

`npm i @ax0107/homebridge-ledstrip-ble` in homebridge terminal
 
You also need to start python script:
`python3 server.py`
(requirements: bleak, fastapi, numpy libraries)

## Configuration
```js
{
    "accessory": "LedStrip", // Dont change
    "name": "LED", // Accessory name
    "uuid": "be320202f8e8" // BLE device UUID
}
```

To find your device uuid, use `hcitool lescan`, grab the device uuid, remove all ':' and use lowercase alpha characters

## Contribution
You can contribute by creating merge request