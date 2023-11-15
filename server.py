
from rgb_control import main as rgb_control_process_main, write_power_off, write_power_on, write_rgb_color, write_rgb_color_and_brightness
from threading import Thread
from asyncio import run
from flask import Flask, request, jsonify

app = Flask(__name__)


Thread(target=run, args=(rgb_control_process_main(),)).start()


@app.route('/set/', methods=['GET', 'POST'])
def set_color_and_brightness():
    data = request.json
    write_rgb_color_and_brightness(data.get('color', '-1'), data.get('brightness', '-1'))

    return jsonify({'status': 'ok'})


@app.route('/set_state/', methods=['GET', 'POST'])
def set_state():
    data = request.json
    if data.get('status') == 'on':
        write_power_on()
    else:
        write_power_off()
    return jsonify({'status': 'ok'})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9988, debug=False)
