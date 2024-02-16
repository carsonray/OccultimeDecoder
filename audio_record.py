import pyaudio
import wave

outputFile = "./recordings/test500_7.wav"
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

pa = pyaudio.PyAudio()
stream = pa.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

print("recording")

frames = []

for i in range(int(RATE * RECORD_SECONDS / CHUNK)):
    data = stream.read(CHUNK)
    frames.append(data)

print("recording complete")

stream.stop_stream()
stream.close()
pa.terminate()

wf = wave.open(outputFile, "wb")
wf.setnchannels(CHANNELS)
wf.setsampwidth(pa.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
