
class Haptics:

    import struct
    from enum import Enum

    # Initialize pressureData and flag
    pressure_data = [0] * 7  # Assuming 7 pressure values as in your C# code
    flag_pressure_data_ready = False

    # Initialize fingerPositionData and flag
    finger_position_data = [0] * 5  # Assuming 5 finger position values as in your C# code
    flag_microtube_data_ready = False

    # Initialize batteryLevel variable
    battery_level = 0.0


    class FunIndex(Enum):
        FI_AIR_PRESSURE = 0x01
        FI_STABLE_PRESSURE_CTRL = 0x02
        FI_SET_PRESSURE_DEPRECATED = 0x03
        FI_SET_PRESSURE = 0x04
        FI_SET_PID = 0x05
        FI_SET_BATTERY_LED = 0x06
        FI_SET_VIBRATION = 0x07
        FI_SET_PULSE = 0x08
        FI_SET_VIB_SPEED = 0x09
        FI_SET_PULSE_SPEED = 0x0a


    class FunList(Enum):
        FI_BMP280 = 0x01
        FI_MICROTUBE = 0x04
        FI_CLUTCHGOTACTIVATED = 0x05
        FI_BATTERY = 0x06

    class Finger(Enum):
        Thumb = 0
        Index = 1
        Middle = 2
        Ring = 3
        Pinky = 4
        Palm = 5

    def __init__(self, whichHand):
        self.whichHand = whichHand
        self.buffer = bytearray(1024)
        self.oneFrame = bytearray(128)
        self.fingerPositionData = [0] * 5
        self.hapticStartPosition = [0.0] * 5
        self.pressureData = [0] * 7
        self.flag_MicrotubeDataReady = False
        self.flag_pressureDataReady = False
        self.encode = Encode()  # Assuming Encode is a class with an instance method

    @staticmethod
    def get_ghost_finger_name(buf):
        ghost_fingers = {
            0: "GhostThumb",
            1: "GhostIndex",
            2: "GhostMiddle",
            3: "GhostRing",
            4: "GhostPinky",
            5: "GhostPalm"
        }
        return ghost_fingers.get(buf, None)

    @staticmethod
    def set_clutch_state(buf_name, buf_state):
        num_array = [0xFF, 0xFF]

        finger_map = {
            "GhostThumb": 0,
            "GhostIndex": 1,
            "GhostMiddle": 2,
            "GhostRing": 3,
            "GhostPinky": 4,
            "GhostPalm": 5
        }

        state_map = {
            "Enter": 0,
            "Stay": 1,
            "Exit": 2
        }

        if buf_name in finger_map:
            num_array[0] = finger_map[buf_name]

        if buf_state in state_map:
            num_array[1] = state_map[buf_state]

        return num_array

    @staticmethod
    def is_hand_valid(whichHand):
        return whichHand in ["Left", "Right"]

    def set_clutch_state_single(self, finger, apply_haptics):
        num_array = [0xFF, 0xFF]
        finger_map = {
            "Thumb": 0,
            "Index": 1,
            "Middle": 2,
            "Ring": 3,
            "Pinky": 4,
            "Palm": 5
        }

        if finger in finger_map:
            num_array[0] = finger_map[finger]

        num_array[1] = 0 if apply_haptics else 2

        if num_array[0] != 0xFF and num_array[1] != 0xFF:
            return num_array
        else:
            print("Invalid parameter")
            return None

    def set_clutch_state_multiple(self, fingers, apply_haptics):
        num_array = []
        state = 0 if apply_haptics else 2

        if state == 0xFF:
            print("Invalid parameter")
            return None

        finger_map = {
            "Thumb": 0,
            "Index": 1,
            "Middle": 2,
            "Ring": 3,
            "Pinky": 4,
            "Palm": 5
        }

        for finger in fingers:
            if finger in finger_map:
                num_array.append([finger_map[finger], state])
            else:
                print("Invalid parameter")
                return None

        return num_array

    def set_haptics_state(self, finger, state):
        # Initialize the list with 2 elements for finger and state
        haptics_state = [0, 0]
    
        # Check the state (True = entering, False = exiting)
        if state:
            haptics_state = [finger, 0]  # Finger enters (0)
        else:
            haptics_state = [finger, 2]  # Finger exits (2)
    
        return haptics_state

    @staticmethod
    def air_pressure_source_control(airPresSourceCtrlStarted, sourcePres):
        try:
            encode_instance = Encode()
            if not airPresSourceCtrlStarted:
                encode_instance.add_u8(1)  # Send start signal
                encode_instance.add_u8(sourcePres)
                data = encode_instance.add_fun(2)
                if len(data) > 0:
                    # Send the data via BLE
                    # await client.write_gatt_char(characteristic_uuid, data)
                    return data
                else:
                    print("Error: Data is empty after encoding")
                encode_instance.clear_list()

            else:
                # Stop air pressure control
                print("Stopping air pressure control...")
                encode_instance.add_u8(0)  # Send stop signal
                encode_instance.add_u8(0)
                data = encode_instance.add_fun(2)  # Add function ID
                if len(data) > 0:
                    # Send the data via BLE
                    # await client.write_gatt_char(characteristic_uuid, data)
                    return data
                else:
                    print("Error: Data is empty after encoding")
                # Clear the buffer after sending data
                encode_instance.clear_list()

        except Exception as e:
            print(f"Error: {e}")

    def hexr_pressure(self, finger, state, intensity, speed):
        # Set the haptics state based on finger and state (enter, stay, exit)
        haptics_state = self.set_haptics_state(finger.value, state)

        # Start encoding the frequency data 0 for normal haptics
        frequency = 0
        self.encode.add_f32(frequency)
        self.encode.add_u8(haptics_state[0])  # which finger
        self.encode.add_u8(haptics_state[1])  # enter, stay or exit

        # Special case: if intensity is 0, pressure should also be 0
        if intensity == 0:
            pressure = 0.0
        else:
            pressure = self.liner_mapping(0.1, 1.0, intensity, 15, 50)

        self.encode.add_f32(pressure)

        # Clamp the speed value and map it to the desired range
        speed = self.clamp(0.1, 1.0, speed)
        speed = self.liner_mapping(0.1, 1.0, speed, 0.1, 1.0) * 100
        self.encode.add_u8(int(speed))

        # Add function identifier (equivalent to Haptics.FunIndex.FI_SET_PRESSURE)
        data = self.encode.add_fun(4)  # FI = 4
        self.encode.clear_list()  # Clear the encoding list for the next operation

        print(f"Finger Type: {finger.name}, Intensity: {intensity}, Pressure: {pressure}, Speed: {speed}")
        return data


    def hexr_vibrations(self, finger, state, frequency, intensity, peakRatio, speed, endIntensity):
        hapticsState =  self.set_haptics_state(finger.value, state)
        if frequency == 0:
            frequency = 0.0
        else:
            frequency = self.clamp(0.1, 2, frequency)
        self.encode.add_f32(frequency)
        self.encode.add_u8(hapticsState[0])             # which finger
        self.encode.add_u8(hapticsState[1])             # enter, stay or exit
        if intensity == 0:
            intensity = 0.0
            pressure = 0.0
        else:
            intensity = self.clamp(0.1, 1.0, intensity)
            pressure = self.liner_mapping(0.1, 1.0, intensity, 15, 50)

        peakRatio = self.clamp(0.2, 0.8, peakRatio)
        peakRatio = peakRatio * 100
        self.encode.add_f32(pressure)
        self.encode.add_u8(int(peakRatio))
        speed = self.clamp(0.1, 1.0, speed)
        speed = self.liner_mapping(0.1, 1.0, speed, 0.1, 1)
        speed *= 100
        self.encode.add_u8(int(speed))
        endPressure = 0
        if endIntensity < 0.1:
            endIntensity = 0
            endPressure = 0
        else:
            endIntensity = self.clamp(0.1, 1.0, endIntensity)
            endPressure = self.liner_mapping(0.1, 1.0, endIntensity, 15, 50)
            
        self.encode.add_f32(endPressure)
        data = self.encode.add_fun(Haptics.FunIndex.FI_SET_VIB_SPEED.value)       # FI = 9
        self.encode.clear_list()

        print(f"Frequency: {frequency}\tPressure: {pressure}\tPeakRatio: {peakRatio}\tSpeed: {speed}")

        return data

    def hexr_vibrations_multiple(self, fingers, states, frequencies, intensities, peakRatios, speeds, endIntensities):
    
        hapticsFrame = bytearray()
    
        for i in range(len(fingers)):
            finger_data = self.hexr_vibrations(
                fingers[i],
                states[i],
                frequencies[i],
                intensities[i],
                peakRatios[i],
                speeds[i],
                endIntensities[i]
            )
            hapticsFrame.extend(finger_data)
    
        return bytes(hapticsFrame)

    def hexr_pressure_multiple(self, fingers, states, intensities, speeds):
        haptics_frame = []

        # Process each finger's data using the hexr_pressure method
        for finger, state, intensity, speed in zip(fingers, states, intensities, speeds):
            haptics_data = self.hexr_pressure(finger, state, intensity, speed)
            haptics_frame.extend(haptics_data)

        # Return the full haptics frame as bytes
        return bytes(haptics_frame)


    def apply_haptics(self, clutchState, targetPres, compensateHysteresis):
        if not Haptics.is_hand_valid(self.whichHand):
            print(f"Invalid hand name: {self.whichHand}")
            return None

        n1 = 0
        if 0 < targetPres < 10:
            n1 = 255  # Equivalent to byte.MaxValue in C#

        presSource = self.pressureData[5]
        valveTiming = HaptGloveValvesCalibrationData.calculate_valve_timing(targetPres, clutchState[0],
                                                                                    presSource, self.whichHand)

        if clutchState[0] == 255 or clutchState[1] == 255:  # Equivalent to checking for byte.MaxValue in C#
            return None

        n2 = valveTiming[0]
        n3 = valveTiming[1]

        # Using the Encode class (similar to the C# Encode.Instance)
        encode = Encode()
        encode.add_u8(n1)
        encode.add_u8(clutchState[0])
        encode.add_u8(clutchState[1])
        encode.add_u8(targetPres)
        encode.add_u8(n2)
        encode.add_u8(n3)
        encode.add_b1(compensateHysteresis)

        numArray = encode.add_fun(3)
        encode.clear_list()

        return numArray

    def decode_glove_data(self, glove_data):
        self.buffer.extend(glove_data)
        while len(self.buffer) >= 5:
            if self.buffer[1] in Haptics.fun_list:
                length = self.buffer[0]
                if len(self.buffer) < length:
                    break

                checksum = 0
                for i in range(length - 1):
                    checksum ^= self.buffer[i]

                if checksum != self.buffer[length - 1]:
                    self.buffer = self.buffer[length:]
                else:
                    self.oneFrame = self.buffer[:length]
                    self.buffer = self.buffer[length:]
                    self.frame_data_analysis(self.oneFrame)
            else:
                self.buffer = self.buffer[1:]

    def frame_data_analysis(self, frame):
        if frame[1] == self.FunList.FI_BMP280:
            self.decode_pressure(frame)
        elif frame[1] in [self.FunList.FI_MICROTUBE, self.FunList.FI_CLUTCHGOTACTIVATED]:
            self.decode_microtube(frame)
        elif frame[1] == self.FunList.FI_BATTERY:
            self.decode_battery_level(frame)


    def decode_pressure(self, frame):
        for i in range(7):
            start = 3 + i * 5  # In your original code: assumes 5 bytes per value
            # If C# is using 4-byte floats, correct offset is 3 + i * 5 → should be 3 + i * 5 **only if** actual frame structure is like that.
            # BUT if the data is packed every 5 bytes, yet only 4 bytes are float, the 5th might be padding or checksum.

            float_bytes = frame[start:start+4]  # Only 4 bytes for float
            self.pressureData[i] = int(struct.unpack('<f', float_bytes)[0])  # '<f' = little-endian float

        self.flag_pressureDataReady = True

    def decode_microtube(self, frame):
        for i in range(5):
            start = 3 + i * 5  # 3, 8, 13, 18, 23
            self.fingerPositionData[i] = int.from_bytes(frame[start:start+4], byteorder="little", signed=True)

        self.flag_MicrotubeDataReady = True

    def decode_battery_level(self, frame):
        # Convert 4 bytes starting from index 3 to float (same as BitConverter.ToSingle in C#)
        import struct
        self.batteryLevel = struct.unpack('<f', frame[3:7])[0]
        
        print(f"Battery Level: {self.batteryLevel}")

    def clamp(self, lower, upper, input):
        if input > upper:
            return upper
        elif input < lower:
            return lower
        else:
            return input

    def liner_mapping(self, pre_bound1, pre_bound2, input, bound1, bound2):
        if pre_bound2 == pre_bound1:
            return 0

        output = (bound2 - bound1) * (input - pre_bound1) / (pre_bound2 - pre_bound1) + bound1
        return output

    def get_vib_intensity(self, frequency, fake_intensity):
        fake_intensity = self.clamp(0.1, 1.0, fake_intensity)
        pressure = 0.0
        peak_ratio = 0.0

        if frequency >= 10:
            pressure = 50.0
            peak_ratio = self.linear_mapping(0.1, 1.0, fake_intensity, 20.0, 50.0)

        elif frequency >= 5:
            pressure = 50.0
            bound1 = self.linear_mapping(5.0, 10.0, frequency, 20.0, 20.0)
            peak_ratio = self.linear_mapping(0.1, 1.0, fake_intensity, bound1, 50.0)

        elif frequency >= 1:
            peak_ratio = 50.0
            pressure = self.linear_mapping(0.1, 1.0, fake_intensity, 15.0, 50.0)

        elif frequency >= 0.1:
            peak_ratio = 50.0
            pressure = self.linear_mapping(0.1, 1.0, fake_intensity, 15.0, 50.0)

        return [pressure, peak_ratio]

import struct

class Encode:
    _instance = None
    
    @staticmethod
    def get_instance():
        if Encode._instance is None:
            Encode._instance = Encode()
        return Encode._instance

    def __init__(self):
        self.list = []

    def clear_list(self):
        self.list.clear()

    def add_fun(self, n):
        b = [0] * 2
        b[0] = len(self.list) + 2
        b[1] = n
        self.list.insert(0, b[1])
        self.list.insert(0, b[0])
        return bytes(self.list)

    def add_u8(self, n):
        b = [0x01, n]  # 0x01 is the header for u8
        self.list.extend(b)
        return bytes(self.list)

    def add_u16(self, n):
        b = [0x02, n & 0xFF, (n >> 8) & 0xFF]  # Little-endian u16
        self.list.extend(b)
        return bytes(self.list)

    def add_u32(self, n):
        b = [0x03]
        for i in range(4):
            b.append(n & 0xFF)
            n >>= 8
        self.list.extend(b)
        return bytes(self.list)

    def add_u64(self, n):
        b = [0x04]
        for i in range(8):
            b.append(n & 0xFF)
            n >>= 8
        self.list.extend(b)
        return bytes(self.list)

    def add_i8(self, n):
        b = [0x05, n]  # 0x05 is the header for i8
        self.list.extend(b)
        return bytes(self.list)

    def add_i16(self, n):
        b = [0x06] + list(n.to_bytes(2, byteorder='little', signed=True))  # Little-endian i16
        self.list.extend(b)
        return bytes(self.list)

    def add_i32(self, n):
        b = [0x07] + list(n.to_bytes(4, byteorder='little', signed=True))  # Little-endian i32
        self.list.extend(b)
        return bytes(self.list)

    def add_i64(self, n):
        b = [0x08] + list(n.to_bytes(8, byteorder='little', signed=True))  # Little-endian i64
        self.list.extend(b)
        return bytes(self.list)

    def add_f32(self, n):
        b = [0x09] + list(bytearray(struct.pack('<f', n)))  # Little-endian f32
        self.list.extend(b)
        return bytes(self.list)

    def add_d64(self, n):
        b = [0x0a] + list(bytearray(struct.pack('<d', n)))  # Little-endian d64
        self.list.extend(b)
        return bytes(self.list)

    def add_b1(self, n):
        b = [0x0b, 0x01 if n else 0x00]  # 0x0b is the header for bool
        self.list.extend(b)
        return bytes(self.list)



class HaptGloveValvesCalibrationData:
    valveCaliOn_Left = [
        [
            [13, 20, 27, 34, 44, 130],
            [12, 18, 25, 32, 42, 130],
            [12, 17, 23, 30, 39, 130],
            [12, 17, 23, 30, 39, 130],
            [13, 18, 24, 31, 40, 130],
            [13, 18, 24, 31, 40, 130]
        ],
        [
            [14, 21, 27, 35, 46, 200],
            [12, 19, 25, 33, 44, 200],
            [12, 17, 24, 31, 41, 200],
            [12, 17, 23, 30, 41, 200],
            [13, 18, 25, 32, 41, 200],
            [13, 18, 25, 32, 41, 200]
        ],
        [
            [14, 21, 28, 36, 48, 255],
            [13, 19, 26, 34, 46, 255],
            [12, 18, 24, 32, 42, 255],
            [12, 18, 24, 31, 42, 255],
            [13, 19, 25, 33, 43, 255],
            [13, 19, 25, 33, 43, 255]
        ],
        [
            [14, 21, 29, 37, 52, 255],
            [13, 20, 27, 36, 49, 255],
            [12, 18, 25, 33, 46, 255],
            [12, 18, 24, 33, 46, 255],
            [13, 19, 26, 35, 47, 255],
            [13, 19, 26, 35, 47, 255]
        ],
        [
            [14, 22, 30, 39, 56, 255],
            [13, 20, 28, 37, 54, 255],
            [12, 19, 25, 34, 54, 255],
            [12, 19, 25, 34, 54, 255],
            [13, 20, 27, 36, 54, 255],
            [13, 20, 27, 36, 54, 255]
        ]
    ]

    valveCaliOff_Left = [
        [100, 130, 160, 190, 210, 230],
        [100, 130, 160, 190, 210, 230],
        [100, 130, 160, 190, 210, 230],
        [100, 130, 160, 190, 210, 230],
        [100, 130, 160, 190, 210, 230],
        [100, 130, 160, 190, 210, 230]
    ]

    valveCaliOn_Right = [
        [
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [7, 13, 22, 36, 50, 255]
        ],
        [
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [7, 13, 22, 36, 50, 255]
        ],
        [
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [7, 13, 22, 36, 50, 255]
        ],
        [
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [8, 15, 25, 40, 80, 255]
        ],
        [
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [3, 4, 5, 6, 8, 20],
            [9, 16, 27, 44, 90, 255]
        ]
    ]

    valveCaliOff_Right = [
        [50, 60, 70, 80, 90, 100],
        [50, 60, 70, 80, 90, 100],
        [50, 60, 70, 80, 90, 100],
        [50, 60, 70, 80, 90, 100],
        [50, 60, 70, 80, 90, 100],
        [60, 80, 110, 130, 160, 200]
    ]

    @staticmethod
    def calculate_valve_timing(tarPres, fingerID, presSource, whichHand):
        if whichHand == "Left":
            valveCaliOn = HaptGloveValvesCalibrationData.valveCaliOn_Left
            valveCaliOff = HaptGloveValvesCalibrationData.valveCaliOff_Left
        elif whichHand == "Right":
            valveCaliOn = HaptGloveValvesCalibrationData.valveCaliOn_Right
            valveCaliOff = HaptGloveValvesCalibrationData.valveCaliOff_Right
        else:
            return None

        index1 = (170000 - presSource) // 2000
        index1 = max(0, min(index1, 4))

        valveSelectedOn = valveCaliOn[index1][fingerID][:]
        valveSelectedOff = valveCaliOff[fingerID][:]

        return HaptGloveValvesCalibrationData.GetValveTiming(tarPres, valveSelectedOn, valveSelectedOff)

    @staticmethod
    def GetValveTiming(tarPres, valveSelectedOn, valveSelectedOff):
        valveTiming = [0, 0]
        if tarPres == 0:
            valveTiming[0] = 0
            valveTiming[1] = 0
        elif tarPres < 10:
            valveTiming[0] = 150
            valveTiming[1] = tarPres
        elif tarPres < 20:
            valveTiming[0] = int(((tarPres - 10) / 10.0) * (valveSelectedOn[1] - valveSelectedOn[0]) + valveSelectedOn[0])
            valveTiming[1] = int(((tarPres - 10) / 10.0) * (valveSelectedOff[1] - valveSelectedOff[0]) + valveSelectedOff[0])
        elif tarPres < 30:
            valveTiming[0] = int(((tarPres - 20) / 10.0) * (valveSelectedOn[2] - valveSelectedOn[1]) + valveSelectedOn[1])
            valveTiming[1] = int(((tarPres - 20) / 10.0) * (valveSelectedOff[2] - valveSelectedOff[1]) + valveSelectedOff[1])
        elif tarPres < 40:
            valveTiming[0] = int(((tarPres - 30) / 10.0) * (valveSelectedOn[3] - valveSelectedOn[2]) + valveSelectedOn[2])
            valveTiming[1] = int(((tarPres - 30) / 10.0) * (valveSelectedOff[3] - valveSelectedOff[2]) + valveSelectedOff[2])
        elif tarPres < 50:
            valveTiming[0] = int(((tarPres - 40) / 10.0) * (valveSelectedOn[4] - valveSelectedOn[3]) + valveSelectedOn[3])
            valveTiming[1] = int(((tarPres - 40) / 10.0) * (valveSelectedOff[4] - valveSelectedOff[3]) + valveSelectedOff[3])
        elif tarPres < 60:
            valveTiming[0] = int(((tarPres - 50) / 10.0) * (valveSelectedOn[5] - valveSelectedOn[4]) + valveSelectedOn[4])
            valveTiming[1] = int(((tarPres - 50) / 10.0) * (valveSelectedOff[5] - valveSelectedOff[4]) + valveSelectedOff[4])
        else:
            valveTiming[0] = valveSelectedOn[5]
            valveTiming[1] = valveSelectedOff[5]
        return valveTiming


Haptics.fun_list = {
    1: 'FI_BMP280',
    4: 'FI_MICROTUBE',
    5: 'FI_CLUTCHGOTACTIVATED'
}
