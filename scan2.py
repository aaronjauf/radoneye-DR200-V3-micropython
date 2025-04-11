# use Thonny's package manager to install aioble
# https://www.elektronik-kompendium.de/sites/raspberry-pi/2808101.htm
# active scan

import aioble
import uasyncio as asyncio

async def bluetooth_scan():
    print('Active Bluetooth-Scan')
    print()
    async with aioble.scan(duration_ms=5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            #print(result, result.device)
            print(result, result.name(), result.rssi, result.services())

asyncio.run(bluetooth_scan())
