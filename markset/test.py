

import tinyweb
import race_matrix
import json

app = tinyweb.webserver()


# Index page
@app.route('/')
@app.route('/index.html')
async def index(req, resp):
    # Just send file
    await resp.send_file('index.html')

@app.route('/markset.js')
async def index(req, resp):
    # Just send file
    await resp.send_file('markset.js', max_age=0)


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
        self.pinColors = []
        # pin = Pin(2, Pin.OUT)   # set GPIO0 to output to drive NeoPixels
        # self.np = NeoPixel(pin, self.num_leds)   # create NeoPixel driver on GPIO0

    def turn_off(self):
        for i in range(self.num_leds):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def randow(self):
        for i in range(self.num_leds - 1, 1, -1):
            self.np[i - 1] = self.np[i]
        self.np[0] = (random.randint(0, 254), random.randint(0, 254), random.randint(0, 254))

    def delete(self, data):
        self.turn_off()
        return {'message': 'changed', 'value': 'off'}

    def put(self, data):
        """Return list of all customers"""
        for i in range(self.num_leds):
            self.np[i] = (0, 0, 0)
        self.np.write()   
        off_timer = Timer(1)
        off_timer.init(mode=Timer.Timer.PERIODIC, period=500, callback=self.randow)  
        return {'message': 'changed', 'value': 'on'}

class FileSystem():
    def post(self, data):
        
        print("fs post:" + str(data))
        return {'result': 'true'}

class LedMatrix():

    def __init__(self):
        self.rows = 10
        self.columns = 60
        self.matrix_data = []
        self.matrix = race_matrix.RaceMatrix(self.rows, self.columns, self.update_matrix)

    def update_matrix(self, data):
        self.matrix_data = data

    def get(self, data):
        return {'rows': self.rows, 'columns': self.columns, 'matrix': self.matrix_data}

    def put(self, data):
        self.matrix.BeginTimer(3)
        return {'result': 'true'}

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

if __name__ == '__main__':
    app.add_resource(Lights, '/api/lights')
    app.add_resource(FileSystem, '/api/files')
    app.add_resource(Status, '/api/status')
    app.add_resource(LedMatrix, '/api/leds')
    print("webserver starting")
    app.run(host='0.0.0.0', port=8082)    