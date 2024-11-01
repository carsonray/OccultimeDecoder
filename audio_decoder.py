import wave
import numpy as np
import time
import datetime
from codecs import decode
import struct
import scipy

class AudioDecoder:
    def __init__(self, file, freq, interval):
        self.file = file
        self.freq = freq
        self.interval = interval
        
        # Opens audio file and gets data
        wf = wave.open(self.file, "rb")
        self.frames = np.frombuffer(wf.readframes(-1), dtype=np.int32)
        self.frame_rate = wf.getframerate()
        wf.close()

    def decode(self, bitThres, size):
        # Sets parameters

        # Theshold for detecting high logic bits
        self.bitThres = bitThres

        # Size of data blocks to decode
        self.size = size

        # Gets locations of wave peaks
        self.wave_peaks = self.get_wave_peaks()

        # Looks for binary signal within ranges to get data
        raw = self.convert_binary(self.wave_peaks, bitThres)

        # Gets locations of data blocks and parses into array
        self.data_stamps = self.locate_data(raw, size)
        self.data = self.parse_data(raw, self.data_stamps, size)

    def get_wave_peaks(self):
        """Gets indices of wave peaks"""
        return scipy.signal.find_peaks(self.frames, distance=0.75*self.frame_rate/self.freq)[0]
        
    def convert_binary(self, index, bitThres):
        """Converts frame amplitudes to binary signal"""
        selected = self.frames[np.array(index)]
        data = np.zeros(selected.size, dtype = np.int8)
        data[selected < bitThres] = 0
        data[selected >= bitThres] = 1

        return data
    
    def locate_data(self, data, size):
        """Finds data chunks of given size"""

        # Finds indices of all 1 bits
        indices = np.argwhere(data)[:, 0]

        # Gets differences between indices
        separation = np.diff(indices)

        # Marks all indices that have a separation of more than data buffer
        stamps = np.delete(indices, np.argwhere(separation <= (size-1)*self.interval) + 1)[1:]

        indices = np.delete(indices, np.argwhere(separation < self.interval) + 1)

        # Gets all indices with enough room for a full data block
        indices = indices[indices <= data.size - (size-1)*self.interval]

        # Restricts to indices with an end bit at the end of the data block
        indices = indices[data[indices + (size-1)*self.interval].astype(np.bool_)]

        # Adds beginnings of data blocks to second stamps
        self.second_stamps = np.sort(np.union1d(stamps, indices))

        return indices
    
    def parse_data(self, data, index, size):
        """Gets array of data chunks from locations"""
        index = np.array(index)

        # Expands indices array to include full data size (excluding repeats)
        indices = index.reshape(-1, 1) + np.arange(0, size*self.interval, self.interval).reshape(1, -1)
        
        # Trims off start and end bits
        return data[indices][:, 1:-1].astype(np.int16)
    
    def get_second(self, index):
        """Finds closest second stamp before frame index"""
        frameDiff = index - np.concatenate(([-1], self.wave_peaks[self.second_stamps]))

        frameDiff[frameDiff < 0] = np.max(frameDiff) + 1
        return np.argmin(frameDiff, axis=0) - 1
    
    def get_micros(self, index):
        """Gets microsecond timestamp from frame index"""
        # Adds placeholder wave peak
        peaks = np.concatenate(([-1], self.wave_peaks), axis=0)

        # Gets differences between index and wave peaks
        frameDiff = np.array(index) - peaks
        
        # Finds closest wave peak before index
        frameDiff[frameDiff < 0] = np.max(frameDiff) + 1
        peakCount = np.argmin(frameDiff, axis=0) - 1

        # Interpolates between wave peaks before and after frame
        if peakCount < frameDiff.size-2:
            peakCount += frameDiff[peakCount+1] / (peaks[peakCount+2]-peaks[peakCount+1])
        
        # Adds placeholder second stamp
        stamps = np.concatenate(([self.second_stamps[0]-self.freq], self.second_stamps), axis=0)

        # Gets differences between peak count and second stamps
        peakDiff = peakCount - stamps

        # Finds difference to closest second stamp before current peak
        peakDiff[peakDiff < 0] = np.max(peakDiff) + 1
        peaksAfter = np.min(peakDiff, axis=0)

        # Converts wave peaks to microseconds
        return int(peaksAfter/self.freq*1000000)
    
    def get_data_object(self, dataFormat, index):
        """Gets closest data object to frame index"""

        # Finds closest data stamp to index
        frameDiff = index - self.wave_peaks[self.data_stamps]

        frameDiff = np.abs(frameDiff)
        dataNum = np.argmin(frameDiff, axis=0)

        # Feeds data to format object
        dataFormat.feed(self.data[dataNum])

        return (dataNum, dataFormat)

    def get_timestamp(self, dataFormat, index):
        """Gets unix timestamp of frame index"""

        # Gets data number and timestamp from closest data object
        dataNum, dataObject = self.get_data_object(dataFormat, index)
        timestamp = dataObject.timestamp()

        # Calculates how many seconds away from timestamp index is
        timeDiff = self.get_second(index) - self.get_second(self.wave_peaks[self.data_stamps[dataNum]])

        return timestamp + timeDiff
    
    def get_audio_offset(self, ppsFrames):
        # Finds closest second stamp to frame index
        frameDiff = ppsFrames.reshape(-1, 1) - self.wave_peaks[self.second_stamps]
        
        absDiff = np.abs(frameDiff)
        return np.mean(frameDiff[np.arange(ppsFrames.size), np.argmin(absDiff, axis=-1)])

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

class StandardDateTime(DataFormat):
    def lat(self):
        return self.bin_to_float(self.bitstring(0, 32))
    def long(self):
        return self.bin_to_float(self.bitstring(32, 64))
    def timestamp(self):
        return int(self.bitstring(64, 96), 2)