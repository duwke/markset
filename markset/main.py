#! /usr/bin/env python3
import asyncio
import board
import gc
import neopixel
from quart import Quart, render_template, request, redirect, url_for, send_from_directory
import socket
import coloredlogs, logging
coloredlogs.install()
import sys, os

import horn
import race_matrix
import race_manager
from boat_control import BoatControl

import datetime 

app = Quart(__name__)
test = False

pixel_pin = board.D21
pixel_width = 60
pixel_height = 10
pixels = neopixel.NeoPixel(pixel_pin, pixel_width * pixel_height, brightness=.9, auto_write=False, pixel_order=neopixel.GRB)
matrix = race_matrix.RaceMatrix(pixels, pixel_width, pixel_height)
horn = horn.Horn()
race_manager = race_manager.RaceManager(matrix, horn)
boat = BoatControl()



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




@app.route('/api/leds', methods=['GET'])
async def led_api():
    if request.method == 'GET':
        matrix_info = matrix.get_matrix()
        return {'rows': matrix_info['rows'], 'columns': matrix_info['columns'], 'matrix': matrix_info['matrix_data']}


@app.route('/api/race/<mode>', methods=['POST'])
async def race_api(mode):
    try:
        if request.method == 'POST':
            if mode == "count_down":
                start_countdown()
            elif mode == "show_order":
                race_manager.begin_show_order()
            elif mode == "stop":
                race_manager.stop()
            elif mode == "begin_race":
                prestart = (await request.get_data()).decode('utf-8')
                logging.debug("got message " + str(prestart))
                race_manager.begin_racing(prestart_sec=int(prestart) * 60)
            elif mode == "single_class":
                single_class = (await request.get_data()).decode('utf-8')
                logging.debug("got message " + str(single_class))
                race_manager.begin_single_class_racing(single_class)
            elif mode == "show_message":
                logging.debug("data " + str(await request.get_data()))
                message = (await request.get_data()).decode('utf-8')
                logging.debug("got message " + str(message))
                race_manager.begin_message(message)
            elif mode == "delay":
                logging.debug("data " + str(await request.get_data()))
                delay = (await request.get_data()).decode('utf-8')
                logging.debug("got message " + str(delay))
                race_manager.begin_delay(int(delay))
            return {'result': 'true'}
    except Exception as inst:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(inst))
        return {'result': 'false'}


@app.route('/api/anchor/<mode>', methods=['POST'])
def anchor_api(mode):
    if request.method == 'POST':
        boat.set_anchor_mode(mode)
        print("set mode2 " + str(mode))
        return {'mode': mode}

@app.route('/api/anchor/status', methods=['GET'])
async def anchor_status_api():
    return str(boat.get_anchor_mode_int())
    

@app.route('/api/computer/<command>', methods=['POST'])
async def computer_control_api(command):
    logging.debug("computer control " + command)
    if request.method == 'POST':
        if command == "shutdown":
            matrix.clear()
            matrix.copy_matrix_to_led()
            os.system('sudo shutdown now')
        elif command == "restart":
            os.system('sudo reboot now')
        elif command == "restart_ros":
            os.system('sudo systemctl restart mavproxy')
            os.system('sudo docker restart mavros')
        return {'result': 'true'}

@app.route('/api/boat/<command>', methods=['POST'])
async def boat_control_api(command):
    logging.debug("boat control " + command)
    if request.method == 'POST':
        if command == "arm":
            boat.arm()
        elif command == "disarm":
            boat.disarm()
        elif command == "horn":
            horn.test()
        return {'result': 'true'}

@app.route('/api/music/<command>', methods=['POST'])
async def music_control_api(command):
    logging.debug("music control " + command)
    if command == "play":
        horn.start_walking_music()
    elif command == "next":
        horn.next_song()
    elif command == "stop":
        horn.stop()
    return {'result': 'true'}

@app.route('/api/boat/<command>', methods=['GET'])
async def boat_status_api(command):
    logging.debug("boat status " + command)
    if command == "voltage":
        return {'result': boat.get_voltage()}

async def start_countdown():
    # assume we are starting the race at 6:15.
    now = datetime.datetime.now()
    race_start = datetime.datetime.now()
    race_start = race_start.replace(hour=18, minute=15)
    logging.debug("race start " + str(race_start))

    difference = (race_start - now)
    total_seconds = difference.total_seconds()
    logging.debug("time till race " + str(total_seconds))

    race_manager.begin_racing(prestart_sec=total_seconds)

@app.before_serving
async def startup():
    app.add_background_task(start_countdown)

@app.after_serving
async def shutdown():
    race_manager.shutdown()

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
    
