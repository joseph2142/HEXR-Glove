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

    # This initiates the pumping of the air into the reservoir.
    async with BleakClient(deviceAddress) as client:
        print(f"Connected to {deviceAddress}")
        reservoirData = haptics.air_pressure_source_control(airPresSourceCtrlStarted, sourcePres)
        await client.write_gatt_char(characteristicUUID, reservoirData)

    clutch_state = haptics.set_clutch_state_single("Index", apply_haptics=True)
    target_pressure = 100  # This is an example, you can adjust the pressure as needed
    # Whether to compensate for hysteresis
    compensate_hysteresis = True
    # Apply the haptics to the Index
    haptics_data = haptics.apply_haptics(clutch_state, target_pressure, compensate_hysteresis)

    # Now we send the haptics data to trigger haptics onto the index finger to the device.
    print(f"Applying haptics to Index Finger: {haptics_data}")
    async with BleakClient(deviceAddress) as client:
        print(f"Connected to {deviceAddress}")
        await client.write_gatt_char(characteristicUUID, bytearray(haptics_data))

    # To disable the haptics, modify the apply_haptics in the clutch state to false and call the
    # apply haptics function again with the modified clutch state.

# Run the BLE connection and control logic
asyncio.run(connect_and_trigger_haptics())
