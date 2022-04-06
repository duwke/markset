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