# markset
An autonomous airboat used for sailboat racing coordination

https://github.com/duwke/markset

# pushing to balena
../balena-cli/balena push markset

# based on python hello world example
https://github.com/balena-io-examples/balena-python-hello-world

# ffmpeg script
ffmpeg -hwaccel opencl -v verbose -filter_complex '[0:0]format=yuv420p,hwupload[a] , [0:5]format=yuv420p,hwupload[b], [a][b]gopromax_opencl, hwdownload,format=yuv420p' -i GS018421.360 -c:v libx264 -pix_fmt yuv420p -map_metadata 0 -map 0:a -map 0:3 GS018421-stitched.mp4

