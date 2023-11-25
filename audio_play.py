import pyaudio
import wave

file = "./Recordings/test1.wav"
CHUNK = 1024

wf = wave.open(file, 'rb')

pa = pyaudio.PyAudio()

stream = pa.open(format=pa.get_format_from_width(wf.getsampwidth()),
                 channels=wf.getnchannels(),
                 rate=wf.getframerate(),
                 output=True)

data = wf.readframes(CHUNK)

while len(data) > 0:
    stream.write(data)

    data = wf.readframes(CHUNK)

stream.stop_stream()
stream.close()

pa.terminate()
