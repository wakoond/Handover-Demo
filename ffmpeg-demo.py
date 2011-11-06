#!/usr/bin/env python

from pyffmpeg import FFMpegReader

## create the reader object
mp=FFMpegReader()

## open an audio-video file
mp.open("your file.mpg")
tracks=mp.get_tracks()

## define a function to be called back each time a frame is read...
def obs(f):
  display(f[2]) # you have to write your display function

tracks[0].set_observer(obs)

mp.run()
