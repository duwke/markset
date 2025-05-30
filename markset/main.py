#! /usr/bin/env python3
import asyncio
import board
import gc
import neopixel
from quart import Quart, render_template, request, redirect, url_for, send_from_directory
import socket
import coloredlogs, logging
coloredlogs.install()
import sys, os, subprocess

import horn
import race_matrix
import race_manager
import datetime 

app = Quart(__name__)
test = False

pixel_pin = board.D21
pixel_width = 60
pixel_height = 20
pixels = neopixel.NeoPixel(pixel_pin, pixel_width * pixel_height, brightness=.9, auto_write=False, pixel_order=neopixel.GRB)
matrix = race_matrix.RaceMatrix(pixels, pixel_width, pixel_height)
horn = horn.Horn()
race_manager = race_manager.RaceManager(matrix, horn)

# Index page
@app.route('/')
async def index():
    return await send_from_directory('.', 'index.html')
@app.route('/static/<path:path>')
async def send_static(path):
    return await send_from_directory('static', path)
@app.route('/markset.js')
async def markset():
    # Just send file
    return await send_from_directory('.', 'markset.js')
# Images
@app.route('/images/<fn>')
async def images(fn):
    return await send_from_directory('static/images', fn)
# pre-gzip all large files (>1k) and then send gzipped version
@app.route('/js/<fn>')
async def files_js(fn):
    resp = await send_from_directory('static/js', '{}.gz'.format(fn))
    resp.headers['Content-Encoding'] = 'gzip'
    return resp
# The same for css files - e.g.
# Raw version of bootstrap.min.css is about 146k, compare to gzipped version - 20k
@app.route('/css/<fn>')
async def files_css(fn):
    resp = await send_from_directory('static/css', '{}.gz'.format(fn))
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





@app.route('/api/leds', methods=['GET'])
async def led_api():
    if request.method == 'GET':
        matrix_info = matrix.get_matrix()
        return {'rows': matrix_info['rows'], 'columns': matrix_info['columns'], 'matrix': matrix_info['matrix_data']}


@app.route('/api/race/<mode>', methods=['POST'])
async def race_api(mode):
    try:
        if request.method == 'POST':
            if mode == "wnr":
                await start_countdown()
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
            elif mode == "stop_message":
                race_manager.stop()
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

async def restart_webserver():
    print("Restart")
    with open("main.py", "a") as a_file:
        a_file.write("#manual restart\n")

@app.route('/api/computer/<command>', methods=['POST'])
async def computer_control_api(command):
    print("computer control " + command)
    if request.method == 'POST':
        if command == "shutdown":
            matrix.clear()
            matrix.copy_matrix_to_led()
            os.system('sudo shutdown now')
        elif command == "restart":
            asyncio.get_event_loop().create_task(restart_webserver())
        elif command == "pull":
            print(os.getcwd())
            print('git result', subprocess.call('git pull', shell=True)) #os.system('git pull'))
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
    elif command == "test":
        horn.test()
    return {'result': 'true'}

async def start_countdown():
    # assume we are starting the race at 6:15.
    now = datetime.datetime.now()
    race_start = datetime.datetime.now()
    race_start = race_start.replace(hour=18, minute=15, second=0) #utc
    print("now " + str(now))
    print("start " + str(race_start))

    difference = (race_start     - now)
    total_seconds = difference.total_seconds()
    print("time till race " + str(total_seconds))

    race_manager.begin_racing(prestart_sec=total_seconds)
    #race_manager.begin_racing(prestart_sec=5)

@app.before_serving
async def startup():
    horn.test()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip_address = s.getsockname()[0]
    finally:
        s.close()

    ip_message = f"Server IP: http://{local_ip_address}"
    print(ip_message)
    race_manager.begin_message(ip_message)
    
    # Show IP message for 15 seconds (optional)
    await asyncio.sleep(15)
    
    app.add_background_task(start_countdown)
    

@app.after_serving
async def shutdown():
    race_manager.shutdown()


if __name__ == "__main__":
    # get the latest config
    print('git fetch ', subprocess.call('git fetch', shell=True)) 
    print('git checkout ', subprocess.call('git checkout FETCH_HEAD -- config.yaml', shell=True)) 
    app.run(host='0.0.0.0', debug=False, port=80)
    
