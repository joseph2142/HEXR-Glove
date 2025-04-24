# HaptGlove Python Project

This project is a Python-based implementation for controlling a Bluetooth-enabled Haptic Glove device. It allows for applying air pressure-based haptics to specific fingers, integrating BLE (Bluetooth Low Energy) for communication with the glove. The project demonstrates how to start air pressure control and apply haptics feedback on various fingers using the `Haptics` class.

## Features

- **Air Pressure Control**: Manages the pumping of air into the glove reservoir to provide pressure feedback to the user's hand.
- **Finger-Specific Haptic Feedback**: Trigger haptics on individual fingers with optional hysteresis compensation.
- **Bluetooth Communication**: Utilizes the `bleak` Python library to connect and send data to the glove device via BLE.
- **Haptics Timing**: Dynamically calculates valve timings to provide accurate and smooth haptic feedback.

## Project Structure

- **`ExampleHaptics.py`**: A sample Python script demonstrating how to establish a BLE connection, control air pressure, and apply haptics to a all finger and removing haptics after 5 sec.
- **`Haptics.py`**: Contains the core logic for interacting with the glove, including applying haptics/vibrations, managing clutch states, and calculating valve timings for air pressure control.
- **`ComprehensiveTestApp.py`**: An interactive Python Script to demonstrate auto BLE connection and allow users to apply custom haptics and custom vibrations to test the glove functions.
  
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
   
## Usage

To use this project, run the `ExampleHaptics.py` script, which will connect to the HaptGlove device, start air pressure control, and apply haptics feedback to the Index finger.

### Steps to Run:

1. **Run the Example Script**:


2. **Explanation of the ExampleHaptics.py**:

    The example demonstrates the following steps:

   - **Connecting to the BLE Device**:
     Using the `bleak` library, we establish a connection with the BLE-enabled glove using its Bluetooth address.

   - **Start Air Pressure Control**:
     The pump is controlled using the `Haptics.air_pressure_source_control()` method. The pressure source is initiated to start pumping air into the reservoir. The example uses a `sourcePres` value of `70`, which is adjustable depending on the pressure needed.

   - **Applying Haptics to Index Finger**:
     The haptics feedback is applied to the index finger using the `apply_haptics()` method. The target pressure is set, and the clutch state is adjusted to enable the haptics.

   - **Haptics Parameters**:
     - `clutch_state`: The state of the clutch for the specified finger (in this case, "Index").
     - `target_pressure`: Defines the level of air pressure to apply to the glove.
     - `compensate_hysteresis`: A boolean value that defines whether to compensate for mechanical hysteresis in the air pressure.

   - **Writing Data to the BLE Characteristic**:
     The script sends data to the glove’s BLE characteristic to trigger haptics on the specified finger. This is done using `write_gatt_char()` to send the haptics data.

### Customization

You can modify the finger that receives haptics feedback by changing the finger parameter in the `set_clutch_state_single()` method. For example, to apply haptics to the thumb, replace `"Index"` with `"Thumb"`.

Similarly, you can adjust the `target_pressure` value and `compensate_hysteresis` flag to fine-tune the haptics behavior.

To remove haptics from a given finger,
you can modify the boolean in the
set_clutch_state function call to False
and then trigger haptics again for the given finger with the target pressure set to zero.

### Troubleshooting

- Ensure that the device's BLE address and characteristic UUID are correct.
  - If you encounter connectivity issues, check if Bluetooth permissions are enabled on your system.
  - Verify that the BLE device is powered on and within range of the computer running the script.
