# Use this file to discover which characteristics are available on the device.
import asyncio
from bleak import BleakClient
deviceAddress = "0E8135D9-3B6C-D7A9-3635-B2DC00C0F53B"  # Replace with your BLE device's address


async def discover_services(address):
    async with BleakClient(address) as client:
        services = await client.get_services()
        for service in services:
            print(f"Service: {service.uuid}")
            for characteristic in service.characteristics:
                print(f"  Characteristic: {characteristic.uuid} | Properties: {characteristic.properties}")

asyncio.run(discover_services(deviceAddress))
