import json
import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from handle_db import handle_progress
# Import hàm get_tmm_instance thay vì tmm
from trading_manager import get_tmm_instance

app = Flask(__name__, template_folder="../", static_folder="../frontend")
CORS(app)

# Sử dụng async_mode='threading' chuẩn cho Windows
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


@app.route("/")
def home():
    return render_template("index.html")


@socketio.on("predict")
def handle_predict(msg):
    sid = msg.get("sid")
    progress = msg.get("progress")
    print(f"_______________{sid}__________________")

    x_pred = handle_progress(progress, isEnd=False)
    print("x_pred:", x_pred)

    # Lấy instance an toàn đa luồng
    tmm = get_tmm_instance()
    tmm.predict(x_pred)

    emit("info", {"sid": sid, "data": tmm.get_all_info()})


@socketio.on("check")
def handle_check(msg):
    result = msg.get("rs")

    tmm = get_tmm_instance()
    tmm.check(result)

    emit("info", {"data": tmm.get_all_info()})


@socketio.on("connect")
def handle_connect(auth=None):
    print("✅ Client connected")
    tmm = get_tmm_instance()
    emit("info", {"data": tmm.get_all_info()})


@socketio.on("disconnect")
def handle_disconnect():
    print("❌ Client disconnected")


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)