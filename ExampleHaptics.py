import asyncio
from bleak import BleakClient
from Haptics import Haptics

deviceAddress = "EC:C9:FF:45:92:86"  # Replace with your BLE device's address
characteristicUUID = "0000ff01-0000-1000-8000-00805f9b34fb"  # Replace with the characteristic UUID for this action

# Function to manage BLE connection and control air pressure
async def connect_and_trigger_haptics():
    airPresSourceCtrlStarted = False  # Initially, the pump has not been yet started.
    sourcePres = 255
    haptics = Haptics(whichHand="Right")

    try:
        # Checkpoint 1: Confirm Haptics object is created
        print(f"Haptics object created for {haptics.whichHand} hand.")

        # This initiates the pumping of the air into the reservoir.
        async with BleakClient(deviceAddress) as client:
            print(f"Connected to {deviceAddress}")

            # Checkpoint 2: Verify connection is established
            print("Connection to BLE device successful.")

            try:
                # Air pressure control
                reservoirData = haptics.air_pressure_source_control(airPresSourceCtrlStarted, sourcePres)
                if not reservoirData:
                    print("Error: Air pressure source control data is empty.")
                    return

                await client.write_gatt_char(characteristicUUID, reservoirData)
                print("Air pressure source control data sent.")

            except Exception as e:
                print(f"Error during air pressure source control: {e}")
                return

            # Define test inputs
            finger = Haptics.Finger.Index
            state = True  # Set to True to generate pressure
            intensity = 0.8
            speed = 1

            try:
                # Checkpoint 4: Verify hexr_pressure data
                print("Calling hexr_pressure to generate haptics data.")
                haptics_data = haptics.hexr_pressure(finger, state, intensity, speed)

                if not haptics_data:
                    print("Error: Generated haptics data is empty or invalid.")
                    return

                # Checkpoint 5: Check generated haptics data
                print(f"Haptics data generated: {haptics_data}")

            except Exception as e:
                print(f"Error during haptics generation: {e}")
                return

    except Exception as e:
        print(f"Error during BLE connection or process: {e}")
        return

    # Now we send the haptics data to trigger haptics onto the index finger to the device.
    try:
        print(f"Applying haptics to Index Finger: {haptics_data}")
        async with BleakClient(deviceAddress) as client:
            print(f"Connected to {deviceAddress}")
            await client.write_gatt_char(characteristicUUID, bytearray(haptics_data))
            # Checkpoint 6: Verify haptics application
            print("Haptics data sent to the device.")
    
    except Exception as e:
        print(f"Error during haptics application: {e}")
        return

# Run the BLE connection and control logic
try:
    asyncio.run(connect_and_trigger_haptics())
except Exception as e:
    print(f"Error running asyncio task: {e}")


