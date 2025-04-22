import asyncio
from bleak import BleakClient
from Haptics import Haptics

deviceAddress = "EC:C9:FF:45:92:86"  # Replace with your BLE device's address
characteristicUUID = "0000ff01-0000-1000-8000-00805f9b34fb"  # Replace with the characteristic UUID for this action

# Async callback function to handle characteristic changes
async def on_characteristic_changed(characteristic, data, haptics):
    # Pass the data to the decode_glove_data function
    haptics.decode_glove_data(data)

async def connect_and_trigger_haptics():
    airPresSourceCtrlStarted = False  # Initially, the pump has not been yet started.
    sourcePres = 255
    haptics = Haptics(whichHand="Right")

    try:
        async with BleakClient(deviceAddress) as client:
            print(f"Connected to {deviceAddress}")
            
            # Fix: wrap the async callback with asyncio.create_task
            await client.start_notify(
                characteristicUUID,
                lambda characteristic, data: asyncio.create_task(on_characteristic_changed(characteristic, data, haptics))
            )
            
            # Define test inputs for haptics (Turning haptics ON)
            fingers = [Haptics.Finger.Thumb, Haptics.Finger.Index, Haptics.Finger.Middle, 
                       Haptics.Finger.Ring, Haptics.Finger.Pinky, Haptics.Finger.Palm]  
            states = [True, True, True, True, True, True]
            intensities = [1, 1, 1, 1, 1, 1]
            speeds = [1, 1, 1, 1, 1, 1]
            
            # Get the haptics data
            haptics_data = haptics.hexr_pressure_multiple(fingers, states, intensities, speeds)
            print("Hex data being sent:", " ".join(f"{byte:02X}" for byte in haptics_data))

            # Attempt to write haptics data to the GATT characteristic
            if client.is_connected:
                await client.write_gatt_char(characteristicUUID, haptics_data)
                print(f"Successfully applied haptics to all fingers")
            else:
                print("Client is not connected!")

            # Wait for 5 seconds before removing pressure
            print("Waiting 5 seconds before removing Pressure...")
            await asyncio.sleep(5)

            # Define test inputs for haptics (Turning haptics OFF)
            states = [False, False, False, False, False, False]
            intensities = [0, 0, 0, 0, 0, 0]
            speeds = [0, 0, 0, 0, 0, 0]
            
            # Get the haptics data to turn it off
            haptics_data = haptics.hexr_pressure_multiple(fingers, states, intensities, speeds)
            print("Hex data being sent:", " ".join(f"{byte:02X}" for byte in haptics_data))

            # Attempt to write haptics data to the GATT characteristic
            if client.is_connected:
                await client.write_gatt_char(characteristicUUID, haptics_data)
                print(f"Successfully removed haptics from {deviceAddress}")
            else:
                print("Client is not connected!")

    except Exception as e:
        print(f"Failed to apply haptics: {e}")
        return False

# Run the BLE connection and control logic
asyncio.run(connect_and_trigger_haptics())




