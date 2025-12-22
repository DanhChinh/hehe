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
    predicts =  PREDICT(x_pred)
    emit('handle_predict', {"predicts": predicts, 'sid': msg.get('sid')}) 


@socketio.on('check')
def handle_check(msg):
    result = msg.get('rs')
    CHECK(result)
    best_matchs = FIND_BEST_MATCHS()
    emit("best_matchs", {'best_matchs': best_matchs})
    emit('handle_predict', {"predicts": ['' for i in range(numOfModel)], 'sid':None}) 

    


@socketio.on('connect')
def handle_connect():
    print('✅ Client connected')
    best_matchs = FIND_BEST_MATCHS()
    emit("best_matchs", {'best_matchs': best_matchs})

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Client disconnected')
    SAVE_MODELS()
    models, LONGS, numOfModel = LOAD()



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)


