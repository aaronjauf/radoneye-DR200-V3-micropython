# Micropython ESP32-C3 Bluetooth - Radoneye RD200 V3
# use Thonny's package manager to install aioble
# use scan2.py to get BLE_ADDR

import aioble
import uasyncio as asyncio
import bluetooth
import struct

BLE_ADDR = "XX:XX:XX:XX:XX:XX"
# from https://github.com/sormy/radoneye/blob/main/KNOWLEDGE_V2.md
SERVICE_UUID = bluetooth.UUID("00001523-0000-1000-8000-00805f9b34fb")

CHAR_COMMAND = bluetooth.UUID(0x1524)
CHAR_STATUS = bluetooth.UUID(0x1525)
CHAR_HISTORY = bluetooth.UUID(0x1526)

COMMAND_STATUS = bytearray([0x40])
COMMAND_HISTORY = bytearray([0x41])

def decode_history(bDat): # pass binary data to this function
    nMessages = bDat[1]
    nMessage = bDat[2]
    nValuesMessage = bDat[3]
    bDatLen = len(bDat)
    bDatLenCalc = 1+3+2*nValuesMessage
    vals = []
    if bDatLen == bDatLenCalc:
        for i in range(4,bDatLen,2):
            vals.append(struct.unpack_from('<H', bDat, i)[0])
        return vals
    else:
        return None

def decode_status(bDat): # pass binary data to this function
    rNow = struct.unpack_from('<H', bDat, 0x21)[0]
    return rNow # radon now in Bq/m^3

async def ble_connect():
    
    while True:
        try:
            device = aioble.Device(aioble.ADDR_PUBLIC, BLE_ADDR)
            connection = await device.connect(timeout_ms=2000)
            mtu = await connection.exchange_mtu(517)
            async with connection:
                service = await connection.service(SERVICE_UUID)
                #async for char in service.characteristics():
                #    print("found", char, char.uuid)
                char_stat = await service.characteristic(CHAR_STATUS)
                char_cmd = await service.characteristic(CHAR_COMMAND)
                char_hist = await service.characteristic(CHAR_HISTORY)
                while connection.is_connected():
                    await char_cmd.write(COMMAND_STATUS)
                    bDat = await char_stat.notified(timeout_ms=1000)
                    rNow = decode_status(bDat)
                    print("Radon now in Bq/m^3", rNow)
                    
                    await char_cmd.write(COMMAND_HISTORY)
                    bDat = await char_hist.notified(timeout_ms=1000)
                    vals = decode_history(bDat)
                    if vals:
                        print("Radion history", vals)

                    await asyncio.sleep_ms(1000)            
        except:
            pass
    
asyncio.run(ble_connect())

