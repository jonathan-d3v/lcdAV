import pyaudio
import numpy as np
import serial
import time

PORT = 'COM6' 
DEVICE_INDEX = 51 

try:
    ser = serial.Serial(PORT, 115200, timeout=1)
    # allow boot up time for board
    time.sleep(2) 
    
    p = pyaudio.PyAudio()
    info = p.get_device_info_by_index(DEVICE_INDEX)
    print(f"--- CONNECTED TO: {info['name']} ---")
    
    CHANNELS = int(info['maxInputChannels'])
    RATE = int(info["defaultSampleRate"])

    stream = p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE,
                    input=True, input_device_index=DEVICE_INDEX, frames_per_buffer=1024)

    print("Listening... (If you see numbers below, Python is working)")

    while True:
        raw_data = stream.read(1024, exception_on_overflow=False)
        data = np.frombuffer(raw_data, dtype=np.int16)
        
        # Audio check: Calculate raw volume
        peak = np.abs(data).max()
        if peak < 100:
            print("Status: SILENCE (Check your Windows Playback device)")
        else:
            # Send a simple test pattern to the Arduino
            test_data = [4] * 16 # Mid-height bars
            ser.write(b'S')
            ser.write(bytes(test_data))
            print(f"Status: SENDING DATA (Peak: {peak})")
            
        time.sleep(0.1)

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
finally:
    if 'p' in locals(): p.terminate()