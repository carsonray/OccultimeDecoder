import cv2
import time
from moviepy.editor import VideoFileClip
from audio_decoder import StandardFormat, AudioDecoder

vf = "./videos/test500_9.mp4"
af = "./recordings/test500_9.wav"

freq = 500
interval = 2
dataSize = 110
bitThres = 2*10**8
dataFormat = StandardFormat()

clip = VideoFileClip(vf)
clip.audio.write_audiofile(af)

print("Decoding audio signal")
decoder = AudioDecoder(af, freq, interval)
afps = decoder.frame_rate

decoder.decode(bitThres, dataSize)

print("Decoding complete")

cap = cv2.VideoCapture(vf)
vfps = cap.get(cv2.CAP_PROP_FPS)
print(f"Video FPS: {vfps:.2f}")
print(f"Audio FPS: {afps}")
delay = int(1000/vfps)

frameRatio = afps/vfps
print(f"Frame Ratio: {frameRatio:.2f}")

frameNum = 0

while (cap.isOpened()):
    success, frame = cap.read()
    if not success:
        break
    
    audioFrame = frameNum*frameRatio
    dataObject = decoder.get_data_object(dataFormat, audioFrame)[1]
    timestamp = decoder.get_timestamp(dataFormat, audioFrame)
    micros = decoder.get_micros(audioFrame)

    cv2.putText(frame, f"Lat: {dataObject.lat():.2f}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)
    cv2.putText(frame, f"Long: {dataObject.long():.2f}", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)
    cv2.putText(frame, f"Time: {time.ctime(timestamp)}", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)
    cv2.putText(frame, f"Micros: {micros}", (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)
    cv2.imshow("Video with Overlay from Audio Signal", frame)

    if cv2.waitKey(delay) & 0xFF == ord('s'):
        break

    frameNum+=1

cap.release()
cv2.destroyAllWindows()