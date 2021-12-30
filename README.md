# markset
An autonomous airboat used for sailboat racing coordination

https://github.com/duwke/markset

# links
https://awesome-micropython.com/

https://github.com/belyalov/tinyweb
https://randomnerdtutorials.com/micropython-ws2812b-addressable-rgb-leds-neopixel-esp32-esp8266/

pymakr extension requires node - curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -


# Starting from scratch

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