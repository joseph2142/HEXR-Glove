import asyncio
from bleak import BleakScanner, BleakClient
from Haptics import Haptics
import socket

characteristicUUID = "0000ff01-0000-1000-8000-00805f9b34fb"  # Replace with the characteristic UUID


async def find_haptglove_address():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    for device in devices:
        if device.name and "haptglove" in device.name.lower():
            print(f"Found HaptGlove: {device.name} @ {device.address}")
            return device.address

    raise Exception("HaptGlove device not found. Make sure it's on and in range.")


def select_fingers(fingers_enum):
    options = list(fingers_enum.items())
    print("\nSelect fingers by index:")
    for i, (name, _) in enumerate(options):
        print(f"[{i}] {name.capitalize()}")

    selection = input("Enter indices (e.g. 0,2,4): ").strip()
    try:
        indices = [int(i.strip()) for i in selection.split(",")]
        selected = [options[i][1] for i in indices if 0 <= i < len(options)]
        return selected
    except Exception as e:
        print(f"Invalid input: {e}")
        return []


def get_single_value_for_all(prompt, count, value_type=float):
    while True:
        raw = input(prompt + f" (Enter a single value): ").strip()
        try:
            value = value_type(raw)
            values = [value] * count
            return values
        except ValueError:
            print("Invalid input. Try again.")

async def listen_for_max_depth(port=5050):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    sock.setblocking(False)

    while True:
        try:
            data, _ = sock.recvfrom(1024)
            value = float(data.decode().strip())
            yield value
        except:
            await asyncio.sleep(0.01)


async def connect_and_interact():
    address = await find_haptglove_address()
    haptics = Haptics(whichHand="Right")

    async def on_characteristic_changed(characteristic, data):
        haptics.decode_glove_data(data)

    try:
        async with BleakClient(address) as client:
            print(f"Connected to {address}")
            await client.start_notify(characteristicUUID, on_characteristic_changed)

            depth_gen = listen_for_max_depth()

            async for max_depth_norm in depth_gen:
                # Clamp depth value to [0, 1] range
                step = 0.1
                intensity = round(max(0.0, min(max_depth_norm, 1.0)) / step) * step
                if intensity < 0.05:
                    continue  # Optional threshold to ignore noise

                speed = 1.0  # Fixed actuation speed, can be tuned
                fingers = [Haptics.Finger.Index]
                states = [1]
                intensities = [intensity]
                speeds = [speed]

                haptics_data = haptics.hexr_pressure_multiple(fingers, states, intensities, speeds)
                print(f"Sending intensity: {intensity:.2f}")
                await client.write_gatt_char(characteristicUUID, haptics_data)

    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(connect_and_interact())






