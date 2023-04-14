from flask import Flask, render_template, request, jsonify, session, redirect, url_for
# from flask_socketio import SocketIO, emit  # pip/pip3 install flask-socketio
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


# flask_sock.Sock(app)

@app.route('/')
def hello():
    return "Hello, World!"


@socketio.event
def my_event(message):
    emit('my response', {'data': 'got it!'})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
