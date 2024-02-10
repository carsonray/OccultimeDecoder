import os
import sys
from moviepy.editor import VideoFileClip

vf = "./videos/test500_3.mp4"
af = "./recordings/test500_3.wav"

clip = VideoFileClip(vf)
clip.audio.write_audiofile(af)