# HexR Python Project 🐍

This project is a Python-based implementation for controlling a Bluetooth-enabled Haptic Glove device. It allows for applying air pressure-based haptics to specific fingers, integrating BLE (Bluetooth Low Energy) for communication with the glove. The project demonstrates how to start air pressure control and apply haptics feedback on various fingers using the `Haptics` class.

## Features

- **Air Pressure Control**: Manages the pumping of air into the glove reservoir to provide pressure feedback to the user's hand.
- **Finger-Specific Haptic Feedback**: Trigger haptics on individual fingers with optional hysteresis compensation.
- **Bluetooth Communication**: Utilizes the `bleak` Python library to connect and send data to the glove device via BLE.
- **Haptics Timing**: Dynamically calculates valve timings to provide accurate and smooth haptic feedback.

## Project Structure 📚

<details>
 <summary>Installation</summary>  
  
## Installation

To run this project, you'll need to clone the repository and install the necessary dependencies.

1. **Clone the Repository**:
   ```
   git clone https://github.com/your-username/HaptGlovePython.git
   cd HaptGlovePython
   ```
2. **Install the requirements**:
    ```
    pip install requriements.txt
3. **Update BLE device Information**:
    ```
    # Use the AddressDiscovery.py file to recover your device's address and then input them into ExampleHaptics.py
   deviceAddress = ""  # Replace with your BLE device's address
    characteristicUUID = "0000ff01-0000-1000-8000-00805f9b34fb"  # Our device's characteristics UUID
</details>
<details>
 <summary> Haptics.py </summary>  

## `Haptics.py` script 
#### The `Haptics.py` script contains the core logic for interacting with the glove, including applying haptics/vibrations, and calculating valve timings for air pressure control.
| Function                  | Description                                 | Input                                                                                                                  |
|--------------------------|---------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| `hexr_pressure`          | Apply pressure to a single finger           | - `finger`: Use the `haptics.Finger` enum to select the finger<br>- `state`: `true` to apply, `false` to release<br>- `intensity`: 0.1 = lightest, 1 = strongest<br>- `speed`: 0.1 = slowest, 1 = fastest |
| `hexr_pressure_multiple` | Apply pressure to multiple fingers          | Same as `hexr_pressure`, but accepts **arrays** for batch processing.                                                 |
| `hexr_vibrations`        | Apply vibration to a single finger          | - `finger`: Use the `haptics.Finger` enum to select the finger<br>- `state`: `true` to apply, `false` to stop<br>- `frequency`: 0.1 = slowest, 2 = fastest<br>- `intensity`: 0.1 = weakest, 1 = strongest<br>- `peakRatio`: 0.2 = smoothest, 0.8 = sharpest<br>- `speed`: 0.1 = slowest, 1 = fastest |
| `hexr_vibrations_multiple` | Apply vibrations to multiple fingers      | Same as `hexr_vibrations`, but accepts **arrays** for batch processing.                                               |


</details>

<details>
 <summary> ExampleHaptics.py </summary>  

## **`ExampleHaptics.py`** script
#### A sample Python script demonstrating how to establish a BLE connection, control air pressure, and apply haptics to a all finger and removing haptics after 5 sec.

To use this project, run the `ExampleHaptics.py` script, which will connect to the HaptGlove device, start air pressure control, and apply haptics feedback to the Index finger.

#### Steps to Run:

1. **Run the Example Script**:


2. **Explanation of the ExampleHaptics.py**:

    The example demonstrates the following steps:

   - **Connecting to the BLE Device**:
     Using the `bleak` library, we establish a connection with the BLE-enabled glove using its Bluetooth address.
     Bluetooth address need to be updated correctly using the above instructions.

   - **On_Characteristic Changed**:
     Establish the data retrieval from characteristic changed from the device.

   - **Applying Haptics**:
     The haptics feedback is applied to the all finger using the `hexr_pressure_multiple()` method.
     The `hexr_pressure_multiple` method takes in 4 parameters
     - fingers = [Haptics.Finger.Thumb, Haptics.Finger.Index, Haptics.Finger.Middle,Haptics.Finger.Ring, Haptics.Finger.Pinky, Haptics.Finger.Palm]
     - states = [True, True, True, True, True, True] : True for trigger haptics , False to not trigger haptics
     - intensities = [1, 1, 1, 1, 1, 1] # 0.1 lowest Intensities and 1 is the Max Intensities
     - speeds = [1, 1, 1, 1, 1, 1] # 0.1 lowest Speed and 1 is the Max Speed

   - **Haptics Parameters**:
     - `clutch_state`: The state of the clutch for the specified finger (in this case, "Index").
     - `target_pressure`: Defines the level of air pressure to apply to the glove.
     - `compensate_hysteresis`: A boolean value that defines whether to compensate for mechanical hysteresis in the air pressure.

   - **Writing Data to the BLE Characteristic**:
     The script sends data to the glove’s BLE characteristic to trigger haptics on the specified finger. This is done using `write_gatt_char()` to send the haptics data.
</details>

</details>

<details>
 <summary> ComprehensiveTestApp.py </summary>  
 
## **`ComprehensiveTestApp.py`** script
#### An interactive Python Script to demonstrate auto BLE connection and allow users to apply custom haptics and custom vibrations to test the glove functions.

#### Run the **`ComprehensiveTestApp.py`** script and follow the console instruction to interact with the programme.
</details>

<details>
 <summary> Troubleshooting</summary>  
 
### Troubleshooting

- Ensure that the device's BLE address and characteristic UUID are correct.
  - If you encounter connectivity issues, check if Bluetooth permissions are enabled on your system.
  - Verify that the BLE device is powered on and within range of the computer running the script.
</details>
