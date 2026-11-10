"""
Jonathan Dias
this is my first github repo that i put a bit of effort into and im really proud of this project,
this is bound to have errors and mistakes so please feel free to give me any criticism as it helps
no matter how harsh it is.

enjoy my work duud

"""




import pyaudio
import numpy as np
import serial
import time

# --- config ---
'''
you NEED to adjust these if you want it to work:
+ set your port to the com port the microcontroller is plugged into
+ find the device index of your audio output or preferably a loopback channel using the device index scanner script

important:
using a loopback channel makes things much easier because it acts as an airport of data kinda
it lets all of it reach the speakers but actually lets us check whats going through
this isnt really possible when using a regular playback channel because theres no way to monitor or record information (unlike a microphone)
the loopback channel treats the output audio as a recording device and lets us tap in to that data you feel me
'''
PORT = 'COM5' 
DEVICE_INDEX = 51
NOISE_FLOOR = 200  # adjust if flickering is present when theres no audio

try:
    # open serial with a handshake
    print(f"Opening {PORT}...")
    ser = serial.Serial(PORT, 115200, timeout=1)
    time.sleep(2) #delay for microcontroller bootup
    ser.flushInput()
    print("Sync Established!")

    p = pyaudio.PyAudio()
    info = p.get_device_info_by_index(DEVICE_INDEX)
    CHANNELS = int(info['maxInputChannels'])
    RATE = int(info["defaultSampleRate"])

    stream = p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE,
                    input=True, input_device_index=DEVICE_INDEX, frames_per_buffer=1024)

    prev_levels = np.zeros(16)
    indices = np.geomspace(4, 512, 17).astype(int)

    while True:
        raw_data = stream.read(1024, exception_on_overflow=False)
        data = np.frombuffer(raw_data, dtype=np.int16)
        
        
        windowed_data = data * np.hanning(len(data))
        fft = np.abs(np.fft.fft(windowed_data))[:512]
        
        output_bytes = []
        
        # --- settings ---
        gain_offset = 65    # increase if bars "blink" too much during silence
        db_range = 60       # higher for smaller bars and lower for bigger reactive bars*
        falloff_rate = 0.93 # this also helps with reactivity
        attack_smooth = 0.6 # 0.0 to 1.0 (lower is smoother, 1.0 is instant)

        for i in range(16):
            start, end = indices[i], indices[i+1]
            
            if start < end:
                val = (np.mean(fft[start:end]) + np.max(fft[start:end])) / 2
                val = max(1e-5, val) 
            else:
                val = 1e-5
            
            #control for balancing the weight of the eq (letting bass and high end of the same volume make the same impact if that makes sense)
            weight = 1.0 + (i * 0.28) 
            
            #i'll be honest i dont really know what this does but i know its a logarithm
            level_db = 20 * np.log10(val * weight + 1)
            
            #adjust gain offset for where the bar shows up to start off
            #makes sure bars stay gone when there isnt any audio
            level = (level_db - gain_offset) / (db_range / 8)
            level = np.clip(level, 0, 8)

            #smoothing
            if level > prev_levels[i]:
                #smooth attack for the bars showing up
                prev_levels[i] = (prev_levels[i] * (1 - attack_smooth)) + (level * attack_smooth)
            else:
                #smooth decay creates falloff so the bars stay on the screen for a noticeable amount
                prev_levels[i] *= falloff_rate
            
            output_bytes.append(int(prev_levels[i]))

        #send data
        ser.write(b'S')
        ser.write(bytes(output_bytes))
        time.sleep(0.02) #capped at 50fps cuz a 16x2 lcd cant really push past that

        # its actually a shame cuz you dont really get that reactive feel when using one of these because of their slow refresh rate
        # i may try adapt this at a larger scale using leds instead of a display module in a cool enclosure or smth

except Exception as e:
    print(f"Error: {e}")

    #print error message with reason
finally:
    if 'ser' in locals(): ser.close()
    if 'p' in locals(): p.terminate()