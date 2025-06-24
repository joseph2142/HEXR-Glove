import asyncio
from bleak import BleakScanner, BleakClient
from Haptics import Haptics
import socket

characteristicUUID = "0000ff01-0000-1000-8000-00805f9b34fb"

# Map UDP port to HaptGlove finger
PORT_FINGER_MAP = {
    5050: Haptics.Finger.Thumb,
    5051: Haptics.Finger.Index,
    5052: Haptics.Finger.Middle,
    #5053: Haptics.Finger.Ring,
}

async def find_haptglove_address():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    for device in devices:
        if device.name and "haptglove" in device.name.lower():
            print(f"Found HaptGlove: {device.name} @ {device.address}")
            return device.address

    raise Exception("HaptGlove device not found. Make sure it's on and in range.")


async def udp_listener(port, depth_queue):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    sock.setblocking(False)

    while True:
        try:
            data, _ = sock.recvfrom(1024)
            value = float(data.decode().strip())
            await depth_queue.put((port, value))
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

            depth_queue = asyncio.Queue()

            # Start UDP listeners
            listeners = [
                asyncio.create_task(udp_listener(port, depth_queue))
                for port in PORT_FINGER_MAP
            ]

            print(f"Listening on ports: {list(PORT_FINGER_MAP.keys())}")

            # Store most recent intensities
            finger_states = {finger: 0.0 for finger in PORT_FINGER_MAP.values()}

            while True:
                port, depth = await depth_queue.get()

                # Clamp and round intensity
                step = 0.1
                intensity = round(max(0.0, min(depth, 1.0)) / step) * step
                finger = PORT_FINGER_MAP[port]

                # Ignore if very small
                if intensity < 0.05:
                    finger_states[finger] = 0.0
                else:
                    finger_states[finger] = intensity

                # Build command for all active fingers
                fingers = []
                states = []
                intensities = []
                speeds = []

                for f in PORT_FINGER_MAP.values():
                    val = finger_states[f]
                    fingers.append(f)
                    if val < 0.05:
                        states.append(0)  # disable haptic
                        intensities.append(0.0)
                        speeds.append(0.0)
                    else:
                        states.append(1)
                        intensities.append(val)
                        speeds.append(1.0)

                haptics_data = haptics.hexr_pressure_multiple(fingers, states, intensities, speeds)
                print(f"Sending → {[f.name for f in fingers]}: {intensities}")
                await client.write_gatt_char(characteristicUUID, haptics_data)
    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(connect_and_interact())
