#!/usr/bin/env python3 
import subprocess 
import sys
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from ffmpegyoutubeoutput import FfmpegYoutubeOutput
import time 
KEY= "t9r4-x6e5-8crh-t1h5-b4wg" 

picam2 = Picamera2()
video_config = picam2.create_video_configuration()
picam2.configure(video_config)
encoder = H264Encoder(10000000)
output = FfmpegYoutubeOutput(KEY)

try: 
  now = time.strftime("%Y-%m-%d-%H:%M:%S") 
  
  picam2.start_recording(encoder, output)
  while True: 
    time.sleep(1)
except KeyboardInterrupt: 
    picam2.stop_recording() 
finally: 
  output.stop() 
  print("Camera safely shut down") 

