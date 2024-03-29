from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from handlers.fft import FFTHandler
from handlers.series import SeriesHandler
from threading import Lock
from streams.mqtt_stream import MQTTStream as Stream


app = Flask(__name__, template_folder="../client/", static_folder="../client/", static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


thread = None
thread_lock = Lock()


def background_thread():
    fft = FFTHandler(socketio)
    series = SeriesHandler(socketio)

    stream = Stream()
    stream.add_handler(fft)
    stream.add_handler(series)
    stream.receive()


@socketio.on('bci:ready')
def handle_test_message(json):
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    print("Bands are ready to send")


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == '__main__':
    print("Websocket server started")
    socketio.run(app)