from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os, json
from mmodel import *
from handle_data import handle_progress
app = Flask(
    __name__,
    template_folder="../",
    static_folder="../src"
    )
CORS(app)  # Bật CORS cho toàn bộ ứng dụng
socketio = SocketIO(app, cors_allowed_origins="*")  # Cho phép tất cả nguồn
@app.route("/")
def home():
    return render_template("index.html")
    
@socketio.on('predict')
def handle_predict(msg):
    print(f"_______________{msg.get('sid')}__________________")
    progress = msg.get('progress')
    x_pred = handle_progress(progress, isEnd=False)
    PREDICT(x_pred)
    emit('info', 
        {
        'sid': msg.get('sid'),
        'data':GET_ALL_INFO()
        })


@socketio.on('check')
def handle_check(msg):
    result = msg.get('rs')
    CHECK(result)
    FIND_BEST_MATCHS()
    emit("info", {'data': GET_ALL_INFO()})

    


@socketio.on('connect')
def handle_connect():
    print('✅ Client connected')
    FIND_BEST_MATCHS()
    emit("info", {'data': GET_ALL_INFO()})

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Client disconnected')



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)


