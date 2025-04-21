import asyncio
from bleak import BleakClient
from Haptics import Haptics

deviceAddress = "EC:C9:FF:45:92:86"  # Replace with your BLE device's address
characteristicUUID = "0000ff01-0000-1000-8000-00805f9b34fb"  # Replace with the characteristic UUID for this action

async def connect_and_trigger_haptics():
    airPresSourceCtrlStarted = False  # Initially, the pump has not been yet started.
    sourcePres = 255
    haptics = Haptics(whichHand="Right")

    try:
        async with BleakClient(deviceAddress) as client:
            print(f"Connected to {deviceAddress}")
            
            # Define test inputs for haptics
            fingers = [
                Haptics.Finger.Thumb,
                Haptics.Finger.Index,
                Haptics.Finger.Middle,
                Haptics.Finger.Ring,
                Haptics.Finger.Pinky,
                Haptics.Finger.Palm  ]
            states = [True, True, True, True, True, True]
            intensities = [1, 1, 1, 1, 1, 1]
            speeds = [1, 1, 1, 1, 1, 1]
            
            # Get the haptics data
            haptics_data = haptics.hexr_pressure_multiple(fingers, states, intensities, speeds)

            print("Hex data being sent:", " ".join(f"{byte:02X}" for byte in haptics_data))

            # Attempt to write haptics data to the GATT characteristic
            try:
                await client.write_gatt_char(characteristicUUID, haptics_data)
                print(f"Successfully applied haptics to {deviceAddress}")
                return True
            except Exception as write_error:
                print(f"Failed to write data: {write_error}")
                return False

    except Exception as e:
        print(f"Failed to apply haptics: {e}")
        return False

# Run the BLE connection and control logic
asyncio.run(connect_and_trigger_haptics())


