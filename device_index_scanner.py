import pyaudio

p = pyaudio.PyAudio()

print("--- AVAILABLE AUDIO DEVICES ---")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Index {i}: {info['name']}")
    print(f"   Max Input Channels: {info['maxInputChannels']}")
    print(f"   Default Sample Rate: {int(info['defaultSampleRate'])}")
    print("-" * 40)

p.terminate()