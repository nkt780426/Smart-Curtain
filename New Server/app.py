from flask import Flask
from flask_socketio import SocketIO
import mqtt_handler
# from flask_cors import CORS, cross_origin

# Tạo các instance
app = Flask(__name__)
socketio = SocketIO(app)
# CORS(app)

if __name__ == '__main__':
    app.run(debug=True)
