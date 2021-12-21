#!/usr/bin/env micropython
"""
MIT license
(C) Konstantin Belyalov 2017-2018
"""
import tinyweb
from machine import Pin
from neopixel import NeoPixel
from machine import Timer
import gc
import machine


# Create web server application
app = tinyweb.webserver()

pins = {4: 'D2',
        5: 'D1',
        12: 'D6',
        13: 'D7',
        14: 'D5',
        15: 'D8',
        16: 'D0'}

# Index page
@app.route('/')
@app.route('/index.html')
async def index(req, resp):
    # Just send file
    await resp.send_file('index.html')


# Images
@app.route('/images/<fn>')
async def images(req, resp, fn):
    # Send picture. Filename - in parameter
    await resp.send_file('static/images/{}'.format(fn),
                         content_type='image/jpeg')

# JS files.
# Since ESP8266 is low memory platform - it totally make sense to
# pre-gzip all large files (>1k) and then send gzipped version
@app.route('/js/<fn>')
async def files_js(req, resp, fn):
    await resp.send_file('static/js/{}.gz'.format(fn),
                         content_type='application/javascript',
                         content_encoding='gzip')


# The same for css files - e.g.
# Raw version of bootstrap.min.css is about 146k, compare to gzipped version - 20k
@app.route('/css/<fn>')
async def files_css(req, resp, fn):
    await resp.send_file('static/css/{}.gz'.format(fn),
                         content_type='text/css',
                         content_encoding='gzip')


class Lights():

    def __init__(self):
        self.data = []
        self.num_leds = 35
        pin = Pin(2, Pin.OUT)   # set GPIO0 to output to drive NeoPixels
        self.np = NeoPixel(pin, self.num_leds)   # create NeoPixel driver on GPIO0

    def turn_off(self):
        for i in range(self.num_leds):
            self.np[i] = (0, 0, 0)
        self.np.write()


    def put(self, data):
        """Return list of all customers"""
        for i in range(self.num_leds):
            self.np[i] = (255, 255, 255)
        self.np.write()   
        off_timer = Timer(1)
        off_timer.init(mode=Timer.ONE_SHOT, period=1000, callback=self.turn_off)  
        return {'message': 'changed', 'value': 'on'}

# RESTAPI: System status
class Status():

    def get(self, data):
        mem = {'mem_alloc': gc.mem_alloc(),
               'mem_free': gc.mem_free(),
               'mem_total': gc.mem_alloc() + gc.mem_free()}
        sta_if = network.WLAN(network.STA_IF)
        ifconfig = sta_if.ifconfig()
        net = {'ip': ifconfig[0],
               'netmask': ifconfig[1],
               'gateway': ifconfig[2],
               'dns': ifconfig[3]
               }
        return {'memory': mem, 'network': net}
    
    def shutdown(self, t):
        print("Restart4")
        app.shutdown()

    def restart(self, t):
        print("Restart4")
        machine.reset()

    def put(self, data):
        """stop the webserver"""
        print("Status put " + str(data['status']))
        if(data['status'] == "off"):
            off_timer = Timer(2)
            off_timer.init(mode=Timer.ONE_SHOT, period=1000, callback= self.shutdown)
        if(data['status'] == "restart"):
            print("Restart")
            off_timer = Timer(2)
            print("Restart2")
            off_timer.init(mode=Timer.ONE_SHOT, period=1000, callback= self.restart)
            print("Restart3")
        
        return {'message': 'changed', 'value': data['status']}

class FileSystem():
    def post(self, data):
        
        print("fs post:" + str(data))
        return {'result': 'true'}

# RESTAPI: GPIO status
class GPIOList():

    def get(self, data):
        res = []
        for p, d in pins.items():
            val = machine.Pin(p).value()
            res.append({'gpio': p, 'nodemcu': d, 'value': val})
        return {'pins': res}


# RESTAPI: GPIO controller: turn PINs on/off
class GPIO():

    def put(self, data, pin):
        # Check input parameters
        if 'value' not in data:
            return {'message': '"value" is requred'}, 400
        # Check pin
        pin = int(pin)
        if pin not in pins:
            return {'message': 'no such pin'}, 404
        # Change state
        val = int(data['value'])
        machine.Pin(pin).value(val)
        return {'message': 'changed', 'value': val}

if __name__ == '__main__':
    app.add_resource(Lights, '/api/lights')
    app.add_resource(FileSystem, '/api/files')
    app.add_resource(Status, '/api/status')
    app.add_resource(GPIOList, '/api/gpio')
    app.add_resource(GPIO, '/api/gpio/<pin>')
    print("webserver starting")
    app.run(host='0.0.0.0', port=80)
