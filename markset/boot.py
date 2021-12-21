# This is script that run when device boot up or wake from sleep.

import network
import uos
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.connect('jannaATkeeverDOTcc', 'KayleePoe')
    while not sta_if.isconnected():
        pass
print(str(sta_if.ifconfig()))

print(str(uos.statvfs('/')))
