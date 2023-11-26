import pyaudio
import wave
import numpy as np
import time
import datetime
from codecs import decode
import struct

class AudioDecoder:
    def __init__(self, file, freq):
        self.file = file
        self.freq = freq
        
        wf = wave.open(self.file, "rb")
        self.frames = np.from_buffer(wf.readframes(-1), dtype=np.int16)
        self.frame_rate = wf.getframerate()
        wf.close()

    def decode(self, waveThres, bitThres, size):
        # Sets parameters
        self.waveThres = waveThres
        self.bitThres = bitThres
        self.size = size

        # Gets wave peaks and binary signal
        self.wave_peaks = self.get_wave_peaks(waveThres)
        raw = self.convert_binary(self.wave_peaks, bitThres)

        # Gets locations of data blocks and parses into array
        self.second_stamps = self.locate_data(raw, size)
        self.data = self.parse_data(raw, self.second_stamps, size)
    
    def get_wave_peaks(self, waveThres):
        """Gets frame indices at or above threshold"""
        return np.argwhere(self.frames >= waveThres)[:, 0]
    
    def convert_binary(self, index, bitThres):
        """Converts frame amplitudes to binary signal"""
        selected = self.frames[np.array(index)]
        data = np.zeros(selected.size)
        data[selected < bitThres] = 0
        data[selected >= bitThres] = 1

        return data
    
    def locate_data(data, size):
        """Finds data chunks of given size"""

        # Finds indices of all 1 bits
        indices = np.argwhere(data)[:, 0]
        print(indices)

        # Gets differences between indices
        separation = np.diff(indices)
        print(separation)

        # Gets indices that have a separation of more than data buffer
        indices = np.delete(indices, np.argwhere(separation <= size) + 1)

        # Removes last index if there is not enough room for a full data buffer
        if indices[-1] > indices.size - size:
            indices = np.delete(indices, -1)

        # Removes indices that do not have an end bit at the end of the buffer
        return np.delete(indices, np.argwhere(np.logical_not(data[indices + size-1])))
    
    def parse_data(data, index, size):
        """Gets array of data chunks from locations"""
        index = np.array(index)

        # Expands indices array to include full data size
        indices = indices.reshape(indices.size, 1) + np.arange(size).reshape(1, size)
        
        # Trims off start and end bits
        return data[indices][:, 1:-1]
    
    def get_micros(self, index):
        """Gets microsecond timestamp from frame index"""
        # Adds placeholder wave peak at the beginning
        peaks = np.concatenate(([-1], self.wave_peaks))

        # Gets differences between index and wave peaks
        frameDiff = np.array(index) - peaks

        # Finds closest wave peak to index
        frameDiff[frameDiff < 0] = np.nan
        peakCount = np.nanargmin(frameDiff, axis=0) - 1

        # Adds placeholder second stamp at the beginning
        stamps = np.concatenate(([self.second_stamps[0] - self.freq], self.second_stamps))

        # Gets differences between peak count and second stamps
        peakDiff = peakCount - stamps

        # Finds difference to closest second stamp
        peakDiff[peakDiff < 0] = np.nan
        peaksAfter = np.nanmin(peakDiff, axis=0)

        # Converts wave peaks to microseconds
        return peaksAfter/self.freq*1000000
    def get_data_object(self, dataFormat, index):
        """Gets closest data object to frame index"""

        # Finds closest second stamp
        frameDiff = index - self.wave_peaks[self.second_stamps]

        frameDiff = np.abs(frameDiff)
        secondNum = np.argmin(frameDiff, axis=0)

        # Feeds data to format object
        dataFormat.feed(self.data[secondNum])

        return dataFormat

    def get_timestamp(self, dataFormat, index):
        """Gets unix timestamp of frame index"""

        # Finds closest second stamp
        frameDiff = index - self.wave_peaks[self.second_stamps]

        frameDiff = np.abs(frameDiff)
        secondNum = np.argmin(frameDiff, axis=0)

        # Feeds data to format object
        dataFormat.feed(self.data[secondNum])
        # Gets unix timestamp
        timestamp = dataFormat.timestamp()

        # Subtracts 1 from timestamp if index was before second stamp
        if index < self.wave_peaks[self.second_stamps[secondNum]]:
            timestamp -= 1

        return timestamp

class DataFormat:
    def feed(self, data):
        self.data = data
    def lat(self):
        pass
    def long(self):
        pass
    def year(self):
        pass
    def month(self):
        pass
    def day(self):
        pass
    def hour(self):
        pass
    def minute(self):
        pass
    def second(self):
        pass
    def datetime(self):
        pass
    def timestamp(self):
        pass
    def bitstring(self, start, end):
        """Converts numpy integer array of ones and zeros to bitstring"""
        return ''.join(str(i) for i in np.flip(self.data[start:end]))
    def bin_to_float(self, b):
        """Converts binary string to float"""
        bf = decode('%%0%dx' % (4 << 1) % int(b, 2), 'hex')[-4:]
        return struct.unpack('>f', bf)[0]

class StandardFormat(DataFormat):
    def lat(self):
        return self.bin_to_float(self.bitstring(0, 32))
    def long(self):
        return self.bin_to_float(self.bitstring(32, 64))
    def year(self):
        return int(self.bitstring(104, 120), 2) + 2000
    def month(self):
        return int(self.bitstring(96, 104), 2)
    def day(self):
        return int(self.bitstring(88, 96), 2)
    def hour(self):
        return int(self.bitstring(80, 88), 2)
    def minute(self):
        return int(self.bitstring(72, 80), 2)
    def second(self):
        return int(self.bitstring(64, 72), 2)
    def datetime(self):
        return datetime.datetime(self.year(), self.month(), self.day(), self.hour(), self.minute(), self.second())
    def timestamp(self):
        return time.mktime(self.datetime().timetuple())