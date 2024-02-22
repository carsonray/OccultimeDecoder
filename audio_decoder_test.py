from audio_decoder import StandardDateTime, AudioDecoder
import time

file = "./recordings/test5000_1.wav"
freq = 5000
interval = 8
decoder = AudioDecoder(file, freq, interval)
decoder.decode(0.75*10**8, 98)

print(decoder.data[0:10])

dataObject = decoder.get_data_object(StandardDateTime(), 200000)[1]
print(dataObject.lat())
print(dataObject.long())
print(time.ctime(dataObject.timestamp()))