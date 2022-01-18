
import adafruit_framebuf
from adafruit_pixel_framebuf import PixelFramebuffer
import asyncio
import board
import gc
import neopixel
from quart import Quart, render_template, request, redirect, url_for, send_from_directory
import socket


import anchorer
import race_matrix
import led_test


app = Quart(__name__)
test = False

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
    resp = await send_from_directory('markset/static/js', '{}.gz'.format(fn))
    resp.headers['Content-Encoding'] = 'gzip'
    return resp

# The same for css files - e.g.
# Raw version of bootstrap.min.css is about 146k, compare to gzipped version - 20k


@app.route('/css/<fn>')
async def files_css(fn):
    print("shit")
    resp = await send_from_directory('markset/static/css', '{}.gz'.format(fn))
    resp.headers['Content-Encoding'] = 'gzip'
    return resp


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
        await asyncio.sleep(1)  # TODO: need to sleep to next full time second
        app.shutdown()

    def put(self, data):
        """stop the webserver"""
        print("Status put " + str(data['status']))
        if(data['status'] == "off"):
            asyncio.get_event_loop().create_task(self.shutdown())

        return {'message': 'changed', 'value': data['status']}


anchor = anchorer.Anchorer()
fb = None
pixel_pin = board.D21
num_pixels = 600
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=.2, auto_write=False, pixel_order=ORDER)
matrix = race_matrix.RaceMatrix(pixels, 60, 10)


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
