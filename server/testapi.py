import requests

requests.post(
    "http://cyan.io.vn/xg79/models_api.php",
    json={
        "model": "Random Forest",
        "session": [0,1,2,3,5,6]
    }
)
