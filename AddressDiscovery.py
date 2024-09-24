# Run this file to discover your device's address. Use that recovered address in the ExampleHaptics.py file
import asyncio
from bleak import BleakScanner


async def discover_devices():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    for device in devices:
        print(f"Device Name: {device.name}, Address: {device.address}, RSSI: {device.rssi}")


# Run the async function to discover devices
asyncio.run(discover_devices())
