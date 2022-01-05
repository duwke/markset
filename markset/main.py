
import board
from neopixel import NeoPixel
import gc
import race_matrix
import anchorer
import random
import asyncio
import socket

from quart import Quart, render_template, request, redirect, url_for, send_from_directory

app = Quart(__name__)

# Index page
@app.route('/')
async def index():
    return await send_from_directory('markset', 'index.html')

@app.route('/static/<path:path>')
async def send_static(path):
    return await send_from_directory('markset/static', path)

@app.route('/markset.js')
async def markset():
    # Just send file
    return await send_from_directory('markset', 'markset.js')

# Images
@app.route('/images/<fn>')
async def images(fn):
    return await send_from_directory('markset/static/images', fn)
                    
# pre-gzip all large files (>1k) and then send gzipped version
@app.route('/js/<fn>')
async def files_js(fn):
    resp =  await send_from_directory('markset/static/js', '{}.gz'.format(fn))
    resp.headers['Content-Encoding'] = 'gzip'
    return resp

# The same for css files - e.g.
# Raw version of bootstrap.min.css is about 146k, compare to gzipped version - 20k
@app.route('/css/<fn>')
async def files_css(fn):
    print("shit")
    resp =  await send_from_directory('markset/static/css', '{}.gz'.format(fn))
    resp.headers['Content-Encoding'] = 'gzip'
    return resp



class Lights():

    def __init__(self):
        self.data = []
        self.num_leds = 35
        self.pinColors = []
        self.np = NeoPixel(board.D18, self.num_leds)   # create NeoPixel driver on GPIO0

    def turn_off(self):
        for i in range(self.num_leds):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def raindow(self):
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
        off_timer.init(mode=Timer.Timer.PERIODIC, period=500, callback=self.ranidow)  
        return {'message': 'changed', 'value': 'on'}



# RESTAPI: System status
class Status():

    def get(self, data):
        mem = {'mem_alloc': gc.mem_alloc(),
               'mem_free': gc.mem_free(),
               'mem_total': gc.mem_alloc() + gc.mem_free()}
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        net = {'ip': local_ip,
               'netmask': '',
               'gateway': '',
               'dns': ''
               }
        return {'memory': mem, 'network': net}
    
    async def shutdown(self):
        print("Restart")
        await asyncio.sleep(1) # TODO: need to sleep to next full time second
        app.shutdown()


    def put(self, data):
        """stop the webserver"""
        print("Status put " + str(data['status']))
        if(data['status'] == "off"):
            asyncio.get_event_loop().create_task(self.shutdown())

        
        return {'message': 'changed', 'value': data['status']}
    

anchor = anchorer.Anchorer()
matrix = race_matrix.RaceMatrix()

@app.route('/api/leds', methods=['GET'])
async def led_api():
    if request.method == 'GET':
        matrix_info = matrix.get_matrix()
        return {'rows': matrix_info['rows'], 'columns': matrix_info['columns'], 'matrix': matrix_info['matrix_data']}

@app.route('/api/race/<mode>', methods=['POST'])
async def race_api(mode):
    if request.method == 'POST':
        if mode == "count_down":
            matrix.begin_countdown(180)
        elif mode == "show_order":
            matrix.begin_show_order()
        elif mode == "begin_race":
            matrix.begin_racing()
        return {'result': 'true'}

@app.route('/api/anchor/<mode>', methods=['POST'])
async def anchor_api(mode):
    if request.method == 'POST':
        if mode == "up":
            await anchor.move()
        if mode == "stop":
            anchor.stop()
        elif mode == "forward":
            anchor.begin_forward()
        elif mode == "reverse":
            anchor.begin_reverse()
        return {'result': 'true'}

        
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)