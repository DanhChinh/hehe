from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os, json
from trading_manager import *
from handle_db import handle_progress 
app = Flask(
    __name__,
    template_folder="../",
    static_folder="../frontend"
    )
CORS(app)  # Bật CORS cho toàn bộ ứng dụng
socketio = SocketIO(app, cors_allowed_origins="*")  # Cho phép tất cả nguồn

tmm = TradingModelManager()

@app.route("/")
def home():
    return render_template("index.html")
    
@socketio.on('predict')
def handle_predict(msg):
    print(f"_______________{msg.get('sid')}__________________")
    progress = msg.get('progress')
    x_pred = handle_progress(progress, isEnd=False)
    print("x_pred:", x_pred)
    tmm.predict(x_pred)
    emit('info', 
        {
        'sid': msg.get('sid'),
        'data':tmm.get_all_info()
        })


@socketio.on('check')
def handle_check(msg):
    result = msg.get('rs')
    tmm.check(result)
    emit("info", {'data': tmm.get_all_info()})


@socketio.on('connect')
def handle_connect(auth=None):
    print('✅ Client connected')
    emit("info", {'data': tmm.get_all_info()})

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Client disconnected')



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)


