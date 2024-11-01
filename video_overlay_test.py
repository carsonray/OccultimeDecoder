import cv2
import time
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip
from audio_decoder import StandardDateTime, AudioDecoder

vf = "./videos/moon2000_8.mp4"
af = "./recordings/moon2000_8.wav"
of = './videos/moon2000_8_overlay.mp4'
audio_of = './videos/moon2000_8_overlay_audio.mp4'

freq = 2000
interval = 8
dataSize = 98
bitThres = 2*10**8
ppsFrames = np.array([36786.75, 80930.85, 125074.95, 169219.05, 213363.15, 257507.25, 301641.35, 345795.45, 389939.55, 434083.65])
dataFormat = StandardDateTime()

clip = VideoFileClip(vf)
clip.audio.write_audiofile(af)

print("Decoding audio signal")
decoder = AudioDecoder(af, freq, interval)
afps = decoder.frame_rate

decoder.decode(bitThres, dataSize)

audioOffset = 0#decoder.get_audio_offset(ppsFrames)
print(f"Audio Offset: {audioOffset:.2f}")

print("Decoding complete")

cap = cv2.VideoCapture(vf)
vfps = cap.get(cv2.CAP_PROP_FPS)
size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

print(f"Video FPS: {vfps:.2f}")
print(f"Audio FPS: {afps}")
delay = int(1000/vfps)

frameRatio = afps/vfps
print(f"Frame Ratio: {frameRatio:.2f}")

frameNum = 0

result = cv2.VideoWriter(of, cv2.VideoWriter_fourcc(*'mp4v'), vfps, size)

print("Overlaying Video")

while (cap.isOpened()):
    success, frame = cap.read()
    if not success:
        break
    
    audioFrame = frameNum*frameRatio - audioOffset
    dataObject = decoder.get_data_object(dataFormat, audioFrame)[1]
    timestamp = decoder.get_timestamp(dataFormat, audioFrame)
    micros = decoder.get_micros(audioFrame)

    cv2.putText(frame, f"Lat: {dataObject.lat():.2f}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)
    cv2.putText(frame, f"Long: {dataObject.long():.2f}", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)
    cv2.putText(frame, f"Time: {time.asctime(time.gmtime(timestamp))}", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)
    cv2.putText(frame, f"Micros: {micros}", (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)
    #cv2.putText(frame, f"Audio Frame: {audioFrame:.2f}", (50, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)

    result.write(frame)

    cv2.imshow("Video Overlay", frame)

    if cv2.waitKey(delay) & 0xFF == ord('s'):
        break

    frameNum+=1

print("Finished overlaying")

cap.release()
result.release()
cv2.destroyAllWindows()

print("Relinking audio")
new_vf = VideoFileClip(of)
new_vf = new_vf.set_audio(clip.audio)
new_vf.write_videofile(audio_of)
print("Finished video export")