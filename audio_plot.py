import wave
import matplotlib.pyplot as plt
import numpy as np

wf1= wave.open("./recordings/test5000_1.wav", "rb")
#wf2= wave.open("./recordings/test500_10.wav", "rb")

frame_rate = wf1.getframerate()
n_frames = wf1.getnframes()
frames1 = wf1.readframes(-1)
#frames2 = wf2.readframes(-1)

wf1.close()

t_audio = n_frames/frame_rate
print("Time:", t_audio)

frame_array1 = np.frombuffer(frames1, dtype=np.int32)
#frame_array2 = np.frombuffer(frames2, dtype=np.int16)

times = np.linspace(0, t_audio, num=n_frames)

plt.figure(figsize=(15,5))
plt.plot(times, frame_array1, color='green')
#plt.plot(times, frame_array2, color='red')
plt.title("Audio Signal")
plt.ylabel("Wave amplitude")
plt.xlabel("Time (s)")
plt.xlim(0, t_audio)
plt.show()