from flask import Flask, request,jsonify
from flask_socketio import SocketIO,emit
from flask_cors import CORS
import time
from threading import Thread,Event
from random import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app,resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app,cors_allowed_origins="*",async_mode='eventlet')
thread = Thread()
thread_stop_event = Event()
num = 0
doorValueStored = -1


def sendDoorStatus():
    print("Door Status")
    doorValue = 4
    socketio.emit("event", {'data': doorValue})
    while not thread_stop_event.isSet():
        if(doorValueStored != doorValue):
            socketio.emit("event", {'data': doorValue})
            print(doorValue)
            doorValueStored = doorValue;
    


@app.route("/http-call")
def http_call():
    """return JSON with string data as the value"""
    data = {'data':'This text was fetched using an HTTP call to server on render'}
    return jsonify(data)

@socketio.on("connect")
def connect():
    print("connected")
    global thread
    if not thread.is_alive():
        print("Starting Thread")
        thread = socketio.start_background_task(sendDoorStatus)


@socketio.on("connected")
def connected():
    """event listener when client connects to the server"""
    global thread
    print(request.sid)
    if not thread.is_alive():
        print("Starting Thread")
        thread = socketio.start_background_task(sendDoorStatus)
    print("client has connected")
    emit("connect",{"data":f"id: {request.sid} is connected"})

@socketio.on('data')
def handle_message(data):
    """event listener when client types a message"""
    print("data from the front end: ",str(data))
    emit("data",{'data':data,'id':request.sid},broadcast=True)

@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the server"""
    print("user disconnected")
    thread_stop_event.set()
    emit("disconnect",f"user {request.sid} disconnected",broadcast=True)


def func(value):
    socketio.emit('event',{'data':value})

if __name__ == '__main__':

    socketio.run(app, debug=True,port=5001)
