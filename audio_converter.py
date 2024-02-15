import pydub
from pydub import AudioSegment

filename = "./recordings/test500_4.m4a"
wav_filename = './recordings/test500_4.wav'

sound = AudioSegment.from_file(filename, format="m4a")
file_handle = sound.export(wav_filename, format='wav')