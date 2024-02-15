import wave
import matplotlib.pyplot as plt
import numpy as np

wf= wave.open("./recordings/test500_5.wav", "rb")

frame_rate = wf.getframerate()
n_frames = wf.getnframes()
frames = wf.readframes(-1)

wf.close()

t_audio = n_frames/frame_rate
print("Time:", t_audio)

frame_array = np.frombuffer(frames, dtype=np.int16)

times = np.linspace(0, t_audio, num=n_frames)

plt.figure(figsize=(15,5))
plt.plot(times, frame_array)
plt.title("Audio Signal")
plt.ylabel("Wave amplitude")
plt.xlabel("Time (s)")
plt.xlim(0, t_audio)
plt.show()