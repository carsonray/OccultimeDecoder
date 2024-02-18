from audio_decoder import StandardFormat, AudioDecoder
import time

file = "./recordings/test500_9.wav"
freq = 500
interval = 2
decoder = AudioDecoder(file, freq, interval)
decoder.decode(2*10**8, 110)

print(decoder.data)

dataObject = decoder.get_data_object(StandardFormat(), 200000)[1]
print(dataObject.lat())
print(dataObject.long())
print(dataObject.year())
print(dataObject.month())
print(dataObject.day())
print(dataObject.hour())
print(dataObject.minute())
print(dataObject.second())
print(time.ctime(dataObject.timestamp()))