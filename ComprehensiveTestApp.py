import asyncio
from bleak import BleakScanner, BleakClient
from Haptics import Haptics

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


async def connect_and_interact():
    address = await find_haptglove_address()
    haptics = Haptics(whichHand="Right")
    fingers_enum = Haptics.Finger.__members__

    async def on_characteristic_changed(characteristic, data):
        haptics.decode_glove_data(data)

    try:
        async with BleakClient(address) as client:
            print(f"Connected to {address}")
            await client.start_notify(characteristicUUID, on_characteristic_changed)

            while True:
                print("\nType '1' to activate haptics, '2' to activate vibrations, '3' to remove pressure or vibration, '4' to get information or '5' to quit.")
                command = input("Command: ").strip().lower()

                if command == "5": #Exit command
                    print("Exiting program...")
                    break

                elif command == "1": #Haptics command
                    fingers = select_fingers(fingers_enum)
                    if not fingers:
                        print("No valid fingers selected.")
                        continue

                    states = [1] * len(fingers)
                    intensities = get_single_value_for_all("Enter intensity for all fingers (0.0 - 1.0)", len(fingers))
                    speeds = get_single_value_for_all("Enter speed for all fingers (0.1 - 1.0)", len(fingers))

                    haptics_data = haptics.hexr_pressure_multiple(fingers, states, intensities, speeds)
                    print("Hex data being sent:", " ".join(f"{b:02X}" for b in haptics_data))
                    await client.write_gatt_char(characteristicUUID, haptics_data)
                    print("Haptics sent.")

                elif command == "2": #Vibrations command
                    fingers = select_fingers(fingers_enum)
                    if not fingers:
                        print("No valid fingers selected.")
                        continue

                    states = [1] * len(fingers)
                    intensities = get_single_value_for_all("Enter intensity for all fingers (0.0 - 1.0)", len(fingers))
                    speeds = get_single_value_for_all("Enter speed for all fingers (0.1 - 1.0)", len(fingers))
                    frequencies = get_single_value_for_all("Enter frequency for all fingers (0.1 - 2.0)", len(fingers))
                    peakratio = get_single_value_for_all("Enter peakratio for all fingers (0.2 - 0.8)", len(fingers))

                    haptics_data = haptics.hexr_vibrations_multiple(fingers, states, frequencies, intensities, peakratio, speeds, intensities)
                    print("Hex data being sent:", " ".join(f"{b:02X}" for b in haptics_data))
                    await client.write_gatt_char(characteristicUUID, haptics_data)
                    print("Haptics sent.")

                elif command == "3": #remove command
                    fingers = list(Haptics.Finger)
                    states = [2] * len(fingers)  # Some devices use 2 for "force stop"
                    intensities = [0] * len(fingers)
                    speeds = [0] * len(fingers)  # Not 1
                    frequencies = [0] * len(fingers)
                    peakratio = [0] * len(fingers)  # Not 0.8

                    haptics_data = haptics.hexr_vibrations_multiple(fingers, states, frequencies, intensities, peakratio, speeds, intensities)
                    await client.write_gatt_char(characteristicUUID, haptics_data)
                    print("All haptics/vibrations stopped.")

                elif command == "4":
                    print("Device Information:")
                    print(f"Battery Level: {haptics.battery_level}%")
                    print(f"Pressure Data: {haptics.pressure_data}%")
                else:
                    print("Unknown command.")

    except Exception as e:
        print(f"Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(connect_and_interact())






