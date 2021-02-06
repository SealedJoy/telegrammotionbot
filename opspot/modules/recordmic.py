import pyaudio, wave, sys
CHUNK = 4096 #16384 #1024 #8192 #4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 9
WAVE_OUTPUT_FILENAME = 'recording1.wav'
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
        channels = CHANNELS,
        rate = RATE,
        input = True,
        input_device_index = 2,
        frames_per_buffer = CHUNK)
print("* recording")
frames = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
   data = stream.read(CHUNK)
   frames.append(data)
print("* done recording")
stream.stop_stream()    # "Stop Audio Recording
stream.close()          # "Close Audio Recording
p.terminate()           # "Audio System Close

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
