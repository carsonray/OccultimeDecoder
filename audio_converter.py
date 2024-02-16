import pydub
from pydub import AudioSegment

old_file = "./recordings/test500_7.mp3"
new_file = './recordings/test500_7_loss.wav'

sound = AudioSegment.from_file(old_file, format="mp3")
file_handle = sound.export(new_file, format='wav')