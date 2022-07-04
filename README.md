# markset
An autonomous airboat used for sailboat racing coordination

https://github.com/duwke/markset



# links
auto hot spot https://www.raspberryconnect.com/projects/157-raspberry-pi-auto-wifi-hotspot-switch-internet

# simple hotspot
sudo nmcli d wifi hotspot ifname wlan1 ssid markus1 password 1234567890
use nmtui to connect to other wireless

# esp as ic2 client for windless
https://github.com/espressif/arduino-esp32/pull/5746/files

# to start the markset process manually
sudo python3 markset/main.py
sudo systemctl restart markset

ffmpeg script
ffmpeg -hwaccel opencl -v verbose -filter_complex '[0:0]format=yuv420p,hwupload[a] , [0:5]format=yuv420p,hwupload[b], [a][b]gopromax_opencl, hwdownload,format=yuv420p' -i GS018421.360 -c:v libx264 -pix_fmt yuv420p -map_metadata 0 -map 0:a -map 0:3 GS018421-stitched.mp4

Setting time for debugging
sudo date +%T -s "11:06:13"

Set rtc clock
sudo hwclock -w