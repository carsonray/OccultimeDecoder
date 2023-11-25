import pyaudio
import wave
import numpy as np

class AudioDecoder:
    def __init__(self, file, freq):
        self.file = file
        self.freq = freq
    def parse(self, waveThres, bitThres):
        wf = wave.open(self.file, "rb")
        frames = np.from_buffer(wf.readFrames(-1), dtype=np.int16)
        frames[frames < waveThres] = 0
        frames[np.logical_and(frames >= waveThres, frames < bitThres)] = 1
        frames[frames >= bitThres] = 2
    def extract(self, frames, chunk):

        

    
    