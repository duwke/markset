#!/bin/sh

udevadm control --reload

#libcamera-hello --list-cameras -n -v
#sleep infinity
libcamera-vid --inline --nopreview -t 0 --width 1024 --height 768 --framerate 15 --codec h264 -o - | ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -thread_queue_size 1024 -use_wallclock_as_timestamps 1 -i pipe:0 -c:v copy -c:a aac -preset medium -strict experimental -f flv rtmp://a.rtmp.youtube.com/live2/t9r4-x6e5-8crh-t1h5-b4wg
#python3 ./loopback.py
