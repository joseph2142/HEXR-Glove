import asyncio
from bleak import BleakClient

device_address = "EC:C9:FF:45:9D:A6"  # Replace with yours

async def main():
    async with BleakClient(device_address) as client:
        print(f"Connected: {client.is_connected}")
        for service in client.services:
            print(f"[Service] {service.uuid}")
            for char in service.characteristics:
                print(f"  [Characteristic] {char.uuid} — Properties: {char.properties}")

asyncio.run(main())
