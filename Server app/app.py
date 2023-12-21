from flask import Flask
from flask_mqtt import Mqtt

# Tạo các instance
app = Flask(__name__)

# Cấu hình log
import logging

    # Tạo đối tượng Logger cho đối tượng 1
logger_broker = logging.getLogger('broker')
file_handler_broker = logging.FileHandler('broker.log')
formatter_broker = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler_broker.setFormatter(formatter_broker)
logger_broker.addHandler(file_handler_broker)
logger_broker.setLevel(logging.INFO)  # Đặt mức độ log theo ý thích

    # Tạo đối tượng Logger cho đối tượng 2
logger_api = logging.getLogger('api')
file_handler_api = logging.FileHandler('api.log')
formatter_api = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler_api.setFormatter(formatter_api)
logger_api.addHandler(file_handler_api)
logger_api.setLevel(logging.INFO)  # Đặt mức độ log theo ý thích

###############################################################################################################################
# Giao tiếp với broker
from config.broker_config import BrokerConfig
app.config.from_object(BrokerConfig)

mqtt = Mqtt(app)

    # Các biến phục vụ routes
esp32_status = False
auto_model = False
auto_responses = {}
alarm_mode = None
alarm_responses = {}

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    logger_broker.info('Connected with result code '+str(rc))
    mqtt.subscribe('esp32_status', qos=2)
    mqtt.subscribe('inform', qos=1)
    mqtt.subscribe('auto_responses', qos=2)
    mqtt.subscribe('alarm_responses', qos=2)

    # In log nếu subcribe thành công
@mqtt.on_subscribe()
def handle_subscribe(client, userdata, mid, granted_qos):
    logger_broker.info('Subscription id {} granted with qos {}.'.format(mid, granted_qos))


    # Xử lý các messages, đọc các hàm xử lý ở dưới
@mqtt.on_message()
def handle_message(client, userdata, message):
    # Kiểm tra xem message.topic là chủ đề nào và thực hiện xử lý tương ứng
    if message.topic == 'inform':
        handle_inform_messages(message)
    if message.topic == 'auto_responses':
        handle_auto_response_messages(message)
    if message.topic == 'alarm_responses':
        handle_alarm_response_messages(message)
    if message.topic == 'esp32_status':
        handle_esp32_status_messages(message)

import json
from flask_socketio import SocketIO

socketio = SocketIO(app)

from pymongo import MongoClient
from config.database_config import DatabaseConfig

    # Tạo DB và collection tương ứng để lưu dữ liệu cảm biến vào MongoDB
client = MongoClient(DatabaseConfig.DATABASE_URI)
db = client['smart_curtain']
inform_collection = db['inform']

def handle_inform_messages(message):
    topic = message.topic
    payload = message.payload.decode('utf-8')
    logger_broker.info(f"Received Message_ID: {message.mid} -- on topic {topic}: {payload}")
    logger_broker.info(f"Begin sent message has id: {message.mid} to websocket name 'inform'!")

    try:
        # gửi message nhận được qua web socket không quan tâm client có nhận được hay không, xử lý thế nào
        socketio.emit('inform', payload)
        logger_broker.info(f"Success sent message has id: {message.mid} to websocket name 'inform'!")

    except Exception as e:
        logger_broker.error(f"Error processing Message_ID: {message.mid} -- Error: {e}")
    
    logger_broker.info(f'Begin save inform message has id: {message.mid} into collection "inform"!')
    try:
        inform = json.loads(payload)

        save_on_db = inform_collection.insert_one(inform)
        if save_on_db.acknowledged:
            logger_broker.info(f'Success save message has id: {message.mid} into collection "inform"')
        else:
            logger_broker.warning(f'Faild to save message has id: {message.mid} into collection "inform"')

    except Exception as e:
        logger_broker.error(f"Error processing Message_ID: {message.mid} -- Error: {e}")

def handle_auto_response_messages(message):
    topic = message.topic
    payload = message.payload.decode('utf-8')
    logger_broker.info(f"Received Message_ID: {message.mid} -- on topic {topic}: {payload}")

    try:
        auto_response = json.loads(payload)
        global auto_model
        if 'correlation_data' in auto_response:
            correlation_data = auto_response['correlation_data']
            global auto_responses
            auto_model = auto_responses[correlation_data] = auto_response['status']
            logger_broker.info(f'Response for request message has correlation_data: {correlation_data} -- {payload}')
        else:
            # Khi chế độ alarm bật thì chế độ auto bị tắt đi, lúc này esp32 sẽ gửi lại 1 gói tin lên topic này và nó không có trường correlation_data
            auto_model = False
            message = json.dumps(False)
            socketio.emit('auto_mode', message)
            logger_broker.info('Auto mode off because alarm mode is on!')

    except Exception as e:
        logger_broker.error(f"Error processing Message_ID: {message.mid} -- Error: {e}")

def handle_alarm_response_messages(message):
    topic = message.topic
    payload = message.payload.decode('utf-8')
    logger_broker.info(f"Received Message_ID: {message.mid} -- on topic {topic}: {payload}")

    try:
        alarm_response = json.loads(payload)
        correlation_data = alarm_response['correlation_data']
        global alarm_responses, alarm_mode
        alarm_mode = alarm_responses[correlation_data] = alarm_response['status']
        logger_broker.info(f'Response for request message has correlation_data: {correlation_data} -- {payload}')

    except Exception as e:
        logger_broker.error(f"Error processing Message_ID: {message.mid} -- Error: {e}")
        
def handle_esp32_status_messages(message):
    topic = message.topic
    payload = message.payload.decode('utf-8')
    logger_broker.info(f"Received Message_ID: {message.mid} -- on topic {topic}: {payload}")

    try:
        data = json.loads(payload)
        activate = data['activate']
        global esp32_status
        esp32_status = activate

        if activate :
            logger_broker.critical(f"Esp32 successfully connected to the broker!")
        else:
            logger_broker.critical(f"Esp32 disconect to the broker!")

    except Exception as e:
        logger_broker.error(f"Error processing Message_ID: {message.mid} -- Error: {e}")

#########################################################################################################
# jwt

from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required, create_access_token, set_access_cookies, unset_jwt_cookies
from config.jwt_config import JwtConfig

app.config.from_object(JwtConfig)
jwt = JWTManager(app)


from flask_restx import Api, Resource, fields
api = Api(app, title='Bạn Hoàng rất đẹp trai!', version='1.0', description='API for controlling smart curtain')

# Tạo model để validate dữ liệu trả về (Swagger)
result_model = api.model('result',{
    'status': fields.Boolean(required=True)
})

error_model = api.model('error',{
    'error': fields.String(required=True)
})

account_model = api.model('account',{
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

# Check thông tin account trong db
users_collection = db['users']

from werkzeug.security import check_password_hash
from flask import jsonify, make_response

# Khi user đăng xuất, xóa token khỏi cookie của họ đồng thời thêm nó vào blasklist để tránh tấn công phát lại
blacklist = set()
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist

# Khi client login, trả về trạng thái đăng nhập thành công hay thất bại. Nếu đăng nhập thành công sẽ set token vào cookie của họ
@api.route('/login')
class LoginResource(Resource):
    @api.doc('Login')
    @api.expect(account_model)
    @api.response(200, 'Success', result_model)
    @api.response(401, 'Faied', error_model)
    def post(self):
        ''''Login account'''
        username = request.json.get('username')
        password = request.json.get('password')

        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            logger_api.info(f"Username: {username} -- is logging in!")

            # Tạo access token và refresh token
            access_token = create_access_token(identity=username)
            print(f"Access token: {access_token}")

            # Thiết lập cookies cho access token và refresh token trực tiếp trên response
            response = make_response(jsonify({"status": True}), 200)
            set_access_cookies(response, access_token)

            logger_api.info(f'Username: {username} -- logged in successfully!')
            return response
        
        logger_api.info(f'Username: {username} -- logged in failed!')
        return {'error': 'Bad username and password'}, 401

# Khi clien logout, trả về trạng thái thành công hay thất bại. Nếu logout thành công, xóa token khỏi cookie đồng thời thêm nó vào blacklist
@api.route('/logout')
class LogoutResource(Resource):
    @jwt_required(optional=True)
    @api.doc('Logout')
    @api.response(200, 'Success', result_model)
    @api.response(401, 'Failed', error_model)
    def post(self):
        ''''Logout account'''
        current_user = get_jwt_identity()
        
        if current_user:
            logger_api.info(f"Username: {current_user} -- is logging out!")

            # Thu hồi token
            jti = current_user.get('jti')  # Sử dụng get để tránh lỗi nếu 'jti' không tồn tại
            if jti:
                blacklist.add(jti)  # Thêm token vào danh sách đen khi đăng xuất
    
            # Xóa cookie liên quan đến jwt
            unset_jwt_cookies(response)
            response = jsonify({'status': True}, 200)

            logger_api.info(f'Username: {current_user} -- Successfully logged out!')
            return response
        else:
            logger_api.info(f'Username: {current_user} -- is not logged in!')
            return {"error": "User is not logged in"}, 401

from werkzeug.security import generate_password_hash

@api.route('/register')
class RegisterResource(Resource):
    @api.doc('Register')
    @api.expect(account_model)
    @api.response(201, 'Success', result_model)
    @api.response(401, 'Failed', error_model)
    def post(self):
        '''Register account'''
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        logger_api.info(f'Creating account for username: {username}.')

        # Kiểm tra xem tên người dùng đã tồn tại chưa
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            logger_api.info(f'Failed to register account for username: {username} -- username already exists.')
            return {"error": "Username already exists"}, 400

        # Hash mật khẩu trước khi lưu vào database
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Đăng ký người dùng mới
        new_user = {'username': username, 'password': hashed_password}
        users_collection.insert_one(new_user)

        response = {"status": "User registered successfully!"}

        logger_api.info(f'Successfully create account for username: {username}!')
        return response, 201

from apscheduler.schedulers.background import BackgroundScheduler
import datetime

# Hàm xóa token đã hết hạn khỏi danh sách đen
def clean_blacklist():
    now = datetime.utcnow()
    expired_tokens = {jti for jti, exp in blacklist if exp < now}
    blacklist.difference_update(expired_tokens)

# Thiết lập tiến trình định kỳ
scheduler = BackgroundScheduler()
scheduler.add_job(clean_blacklist, 'interval', minutes=30)  # Cập nhật mỗi 30 phút
scheduler.start()

##########################################################################################################

# Các api
    
auto_model = api.model('auto',{
    'status': fields.Boolean(required=True),
    'percent': fields.Integer(required=True)
})

alarm_model = api.model('alarm',{
    'status': fields.Boolean(required=True),
    'time': fields.DateTime(required=True),
    'percent': fields.Float(required=True)
})

status_model = api.model('status',{
    'auto': fields.Nested(auto_model),
    'alarm': fields.Nested(alarm_model)
})

@api.route('/status')
class StatusResource(Resource):
    @jwt_required(optional=True)
    @api.doc('get status curtain mode')
    @api.response(200, 'Success', status_model)
    @api.response(401, 'User is not loggeg in', error_model)
    @api.response(501, 'Esp32 disconnect to broker', error_model)
    def get(self):
        ''''Get status curtain mode'''
        current_user = get_jwt_identity()
        
        if current_user:
            logger_api.info(f'Username: {current_user} -- GET "/status"')
            global esp32_status

            if esp32_status:
                global auto_model, alarm_mode
                auto_status = {'status': auto_model}
                alarm_status = {'status': alarm_mode['status'], 'time': alarm_mode['time'], 'percent': alarm_mode['percent']}
                response = {'auto': auto_status, 'alarm': alarm_status}
                logger_api.info(f'Username: {current_user} -- Response for GET "/status": 200 {response}')
                return response, 200
            
            response = {'error': "Esp32 disconnect to broker!"}
            logger_api.info(f'Username: {current_user} -- Response for GET "/status": 501 {response}')
            return response, 501
        
        else:
            response = {"error": "User is not logged in"}
            logger_api.info(f'Username: {current_user} -- Response for GET "/status": 401 {response}')
            return response, 401

from flask import request
import uuid
from threading import Thread, Event
import time

@api.route('/auto')
class AutoModeResource(Resource):
    @jwt_required(optional=True)
    @api.doc('auto mode', params={'status': 'Turn on or off auto mode!', 'percent':'openess'})
    @api.expect(auto_model)
    @api.response(201, 'Success', result_model)
    @api.response(401, 'User is not loggeg in', error_model)
    @api.response(501, 'Esp32 disconnect to broker', error_model)
    def post(self):
        ''''Adjust auto mode and handle curtain'''
        current_user = get_jwt_identity()
        if current_user:
            data = request.get_json()
            logger_api.info(f'Username: {current_user} -- POST "/auto" with payload {data}')
            global esp32_status

            if esp32_status:
                message = {}
                message['status'] = data.get('status')
                message['percent'] = data.get('percent')
                correlation_data = str(uuid.uuid4())
                message['correlation_data'] = correlation_data
                message_json = json.dumps(message)

                global mqtt
                mqtt.publish('auto_requests', message_json, qos = 2)

                # Set sự kiện đợi response trở về
                has_response = Event()
                wait_for_response_thread = Thread(target =wait_for_auto_response, args = (has_response, correlation_data))
                wait_for_response_thread.start()

                # đợi đến khi thành công
                has_response.wait()
                # Reset the event for the next API request
                has_response.clear()

                global auto_responses
                status = auto_responses[correlation_data]
                del auto_responses[correlation_data]
                response = {'status': status}
                logger_api.info(f'Username: {current_user} -- Response for POST "/auto": 201 {response}')
                return response, 201
            
            response = {'error': "Esp32 disconnect to broker!"}
            logger_api.info(f'Username: {current_user} -- Response for POST "/auto": 501 {response}')
            return response, 501
        else:
            response = {"error": "User is not logged in"}
            logger_api.info(f'Username: {current_user} -- Response for POST "/auto": 401 {response}')
            return response, 401

# đợi response từ mqtt
def wait_for_auto_response(has_response, correlation_data):
    global auto_responses
    while correlation_data not in auto_responses:
        time.sleep(0.1)
    # Đánh thức
    has_response.set()

@api.route('/alarm')
class AlarmModeResource(Resource):
    @jwt_required(optional=True)
    @api.doc('alarm mode', params={'status': 'Turn on or off alarm mode!', 'time': 'Time to set curtain','percent':'openess'})
    @api.expect(alarm_model)
    @api.response(201, 'Success', result_model)
    @api.response(401, 'User is not loggeg in', error_model)
    @api.response(501, 'Esp32 disconnect to broker', error_model)
    def post(self):
        ''''Adjust alarm mode and handle curtain'''
        current_user = get_jwt_identity()
        if current_user:
            data = request.get_json()
            logger_api.info(f'Username: {current_user} -- POST "/alarm" with payload {data}')
            global esp32_status

            if esp32_status:
                message = {}
                message['status'] = request.json.get('status')
                message['time'] = request.json.get('time')
                message['percent'] = request.json.get('percent')
                correlation_data = str(uuid.uuid4())
                message['correlation_data'] = correlation_data
                message_json = json.dumps(message)

                global mqtt
                mqtt.publish('alarm_requests', message_json, qos = 2)

                # Set sự kiện đợi response trở về
                has_response = Event()
                wait_for_response_thread = Thread(target =wait_for_alarm_response, args = (has_response, correlation_data))
                wait_for_response_thread.start()

                # đợi đến khi thành công
                has_response.wait()
                # Reset the event for the next API request
                has_response.clear()

                global alarm_responses
                status = alarm_responses[correlation_data]
                del alarm_responses[correlation_data]
                response = {'status': status}
                logger_api.info(f'Username: {current_user} -- Response for POST "/alarm": 201 {response}')
                return response, 201

            response = {'error': "Esp32 disconnect to broker!"}
            logger_api.info(f'Username: {current_user} -- Response for POST "/alarm": 501 {response}')
            return response, 501
        else:
            response = {"error": "User is not logged in"}
            logger_api.info(f'Username: {current_user} -- Response for POST "/alarm": 401 {response}')
            return response, 401


# đợi response từ mqtt
def wait_for_alarm_response(has_response, correlation_data):
    global alarm_responses
    while correlation_data not in alarm_responses:
        time.sleep(0.1)
    # Đánh thức
    has_response.set()

if __name__ == '__main__':
    app.run(debug=True)
