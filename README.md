# markset
An autonomous airboat used for sailboat racing coordination

https://github.com/duwke/markset




# starting from scratch on raspberry pi 3b
sudo apt update
sudo apt upgrade --fix-missing
https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pisudo 

https://learn.adafruit.com/easy-neopixel-graphics-with-the-circuitpython-pixel-framebuf-library/import-and-setup




# Starting from scratch on esp32

esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32spiram-20210902-v1.17.bin

- turn on wifi
import network

wlan = network.WLAN(network.STA_IF) # create station interface
wlan.active(True)       # activate the interface
wlan.connect('essid', 'password') # connect to an AP
wlan.ifconfig()         # get the interface's IP/netmask/gw/DNS addresses

- turn on webrepl
import webrepl_setup

- sync markset
./webreplcmd --host 10.0.0.81 --password markset sync ../markset

# testing on ubuntu
clone mycropython
edit ports/unix makefile to use dev instead of standard.
```sudo ~/workspace/micropython/ports/unix/micropython-dev -m test```

# links
https://awesome-micropython.com/

https://github.com/belyalov/tinyweb
https://randomnerdtutorials.com/micropython-ws2812b-addressable-rgb-leds-neopixel-esp32-esp8266/

pymakr extension requires node - curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -

# esp32 client 
https://github.com/espressif/arduino-esp32/pull/5746/files
