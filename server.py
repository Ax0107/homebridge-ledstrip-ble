
from rgb_control import main as rgb_control_process_main
from threading import Thread
from asyncio import run
from flask import Flask, request, jsonify

app = Flask(__name__)


Thread(target=run, args=(rgb_control_process_main(),)).start()

@app.route('/set', methods=['GET', 'POST'])
def set_color_and_brightness():
    print(request.data)
    return jsonify({'status': 'ok'})


@app.route('/set_state', methods=['GET', 'POST'])
def set_state():
    print(request.data)
    return jsonify({'status': 'ok'})


