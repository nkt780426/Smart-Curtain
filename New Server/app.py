from flask import Flask
from flask_socketio import SocketIO
import mqtt_handler

# Tạo các instance
app = Flask(__name__)
socketio = SocketIO(app)

if __name__ == '__main__':
    app.run(debug=True)
