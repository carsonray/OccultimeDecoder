import os
import sys
from moviepy.editor import VideoFileClip

vf = "./videos/test500_1.mp4"
af = "./recordings/test500_1.wav"

clip = VideoFileClip(vf)
clip.audio.write_audiofile(af)