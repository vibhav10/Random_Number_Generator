from flask import Flask, render_template, request
from flask_socketio import SocketIO
import threading
import time
import random as r
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
cors = CORS(app, resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

class Task(threading.Thread):
    def __init__(self, lb, ub, refreshTime, displayLocation, color):
        threading.Thread.__init__(self)
        self.lb = lb
        self.ub = ub
        self.refreshTime = refreshTime
        self.displayLocation = displayLocation
        self.color = color
        self.num = None
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.num = r.randint(self.lb, self.ub)
            socketio.emit('update', {'id': self.displayLocation, 'num': self.num, 'color': self.color})
            time.sleep(self.refreshTime)

    def stop(self):
        self.running = False

tasks = [
    Task(10, 20, 10, 'D1', 'red'),
    Task(-10, 10, 20, 'D2', 'green'),
    Task(-100, 0, 8, 'D3', 'blue'),
    Task(0, 20, 12, 'D4', 'orange'),
    Task(-40, 40, 16, 'D5', 'purple'),
    Task(100, 200, 14, 'D6', 'pink')
]

for task in tasks:
    task.start()

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@socketio.on('submit')
def handle_submit(form_data):
    form_dict = dict(request.values)
    displayLocation = form_dict['displayLocation']
    lb = int(form_dict['lb'])
    ub = int(form_dict['ub'])
    refreshTime = int(form_dict['refreshTime'])
    color = form_dict['color']
    for task in tasks:
        if task.displayLocation == displayLocation:
            task.lb = lb
            task.ub = ub
            task.refreshTime = refreshTime
            task.color = color

@socketio.on_error
def error_handler(e):
    print(e)

@socketio.on_error_default
def default_error_handler(e):
    print(e)


if __name__ == '__main__':
    socketio.run(app, debug=True)
