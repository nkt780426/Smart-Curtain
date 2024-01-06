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
auto_mode = False
auto_responses = {}
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
        global auto_mode
        correlation_data = auto_response['correlation_data']
        global auto_responses
        auto_mode = auto_responses[correlation_data] = auto_response['status']
        logger_broker.info(f'Response for request message has correlation_data: {correlation_data} -- {payload}')
    except Exception as e:
        logger_broker.error(f"Error processing Message_ID: {message.mid} -- Error: {e}")

def handle_alarm_response_messages(message):
    topic = message.topic
    payload = message.payload.decode('utf-8')
    logger_broker.info(f"Received Message_ID: {message.mid} -- on topic {topic}: {payload}")

    try:
        alarm_response = json.loads(payload)
        correlation_data = alarm_response['correlation_data']
        global alarm_responses
        alarm_responses[correlation_data] = alarm_response['status']
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
        socketio.emit('esp32_status', payload)

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

alarm_responses_model = api.model('alarm_responses',{
    'type': fields.String(required=True),
    'job_id': fields.String(required=True)
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
            response = make_response(jsonify({"status": True, "access_token": access_token}), 200)
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
scheduler = BackgroundScheduler(timezone='Asia/Ho_Chi_Minh')
scheduler.add_job(clean_blacklist, 'interval', minutes=30)  # Cập nhật mỗi 30 phút
scheduler.start()

##########################################################################################################

# Các api
    
auto_model = api.model('auto',{
    'status': fields.Boolean(required=True),
    'percent': fields.Integer(required=True)
})

daily_alarm_model = api.model('daily_alarm',{
    'percent': fields.Float(required=True, description='openess'),
    'hours': fields.Integer(required=True, description='hours'),
    'minutes': fields.Integer(required=True, description='minutes')
})

once_alarm_model = api.model('once_alarm',{
    'percent': fields.Float(required=True, description='openess'),
    'specify_time': fields.String(required=True, description='Time to alarm')
})

cancel_alarm_model = api.model('cancel_alarm',{
    'type': fields.String(required=True),
    'job_id': fields.String(required=True)
})

status_model = api.model('status',{
    'auto': fields.Nested(auto_model),
    'daily_alarm': fields.List(fields.Nested(daily_alarm_model)),
    'once_alarm': fields.List(fields.Nested(once_alarm_model))
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
                global auto_mode, daily_alarm_collections, once_alarm_collections
                auto_status = {'status': auto_mode}

                daily_alarms_cursor = daily_alarm_collections.find({"username": current_user})
                daily_alarms = [daily_alarm for daily_alarm in daily_alarms_cursor]

                once_alarms_cursor = once_alarm_collections.find({"username": current_user})
                once_alarms = [once_alarm for once_alarm in once_alarms_cursor]

                response = {'auto': auto_status, 'daily_alarm': daily_alarms, 'once_alarm': once_alarms}
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
                # Tạo gói tin gửi đi esp32
                message = {}
                message['status'] = data.get('status')
                message['percent'] = data.get('percent')
                correlation_data = str(uuid.uuid4())
                message['correlation_data'] = correlation_data
                message_json = json.dumps(message)

                global mqtt
                mqtt.publish('auto_requests', message_json, qos = 2)
                logger_broker.info(f'Send message has correlation data : {correlation_data} -- payload: {message_json}')

                # Đợi esp32 phản hồi
                has_response = Event()
                wait_for_response_thread = Thread(target =wait_for_auto_response, args = (has_response, correlation_data))
                wait_for_response_thread.start()

                # ESP32 phản hồi thành công
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

# ---------------------  Alarm and handle curtain api -------------------------------------------

# Mỗi khi đến giờ publish 1 message đến esp32
def send_alarm_message_to_esp32(percent):
    # Tạo message gửi đi esp32
    message = {}
    message['percent'] = percent
    correlation_data = str(uuid.uuid4())
    message['correlation_data'] = correlation_data
    message_json = json.dumps(message)

    global mqtt
    mqtt.publish('alarm_requests', message_json, qos = 2)
    logger_broker.info(f'Send message has corrrelation data: {correlation_data} -- payload: {message_json}')

    # Đợi message từ esp32
    has_response = Event()
    wait_for_response_thread = Thread(target =wait_for_alarm_response, args = (has_response, correlation_data))
    wait_for_response_thread.start()
    has_response.wait()
    # Reset the event for the next API request
    has_response.clear()

    # Sau khi esp32 phản hồi
    global alarm_responses
    del alarm_responses[correlation_data]

# đợi response từ broker
def wait_for_alarm_response(has_response, correlation_data):
    global alarm_responses
    while correlation_data not in alarm_responses:
        time.sleep(0.1)
    # Đánh thức
    has_response.set()

# Tạo job với 2 kiểu alarm
from apscheduler.triggers.cron import CronTrigger

daily_alarm_collections = db['daily_alarm']
def create_daily_alarm(username, percent, hours, minutes):
    # Kiểm tra giá trị của hours và minutes
    if 0 <= hours <= 23 and 0 <= minutes <= 59:
        cron_expression = f"{minutes} {hours} * * *"
        trigger = CronTrigger.from_crontab(cron_expression)
        job = scheduler.add_job(send_alarm_message_to_esp32, args=[percent], trigger=trigger)

        alarm_data = {
                "username": username,
                "percent": percent,
                "hours": hours,
                "minutes": minutes,
                "job_id": str(job.id)  # Convert ObjectId sang str để lưu vào MongoDB
        }
        daily_alarm_collections.insert_one(alarm_data)
        return job.id
    else:
        return None  # Hoặc có thể trả về một giá trị đặc biệt để biểu thị lỗi, ví dụ: -1

from apscheduler.triggers.date import DateTrigger
import pytz

once_alarm_collections = db['once_alarm_collections']
def create_once_alarm(username, percent, iso_time):
    try:
        time_utc = datetime.fromisoformat(iso_time)
        time_vietnam = time_utc.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))

        trigger = DateTrigger(run_date=time_vietnam)
        job = scheduler.add_job(send_alarm_message_to_esp32, args=[percent], trigger=trigger)

        alarm_data = {
                "username": username,
                "percent": percent,
                "iso_time": str(iso_time),
                "job_id": str(job.id)  # Convert ObjectId sang str để lưu vào MongoDB
        }
        once_alarm_collections.insert_one(alarm_data)
        return job.id
    except Exception as e:
        return str(e)

@api.route('/daily_alarm')
class DailyAlarmResource(Resource):
    @jwt_required(optional=True)
    @api.doc('daily alarm mode', params={'percent':'openess', 'hours':'hour', 'minutes':'minute'})
    @api.expect(daily_alarm_model)
    @api.response(201, 'Success', alarm_responses_model)
    @api.response(400, 'Wrong date format', error_model)
    @api.response(401, 'User is not log in', error_model)
    @api.response(501, 'Esp32 disconnect to broker', error_model)
    def post(self):
        ''''Daly alarm mode curtain'''
        current_user = get_jwt_identity()
        if current_user:
            data = request.get_json()
            logger_api.info(f'Username: {current_user} -- POST "/daily_alarm" with payload {data}')
            global esp32_status

            if esp32_status:
                job_id=create_daily_alarm(current_user, data['percent'], data['hours'], data['minutes'])
                if job_id is not None:
                    response = {'status': "true", 'job_id': job_id}
                    logger_api.info(f'Username: {current_user} -- Response for POST "/daily_alarm": 201 {response}')
                    return response, 201
                
                response = {'error': "Wrong date format"}
                logger_api.info(f'Username: {current_user} -- Response for POST "/daily_alarm": 400 {response}')
                return response, 400
            
            response = {'error': "Esp32 disconnect to broker!"}
            logger_api.info(f'Username: {current_user} -- Response for POST "/daily_alarm": 501 {response}')
            return response, 501

        response = {"error": "User is not logged in"}
        logger_api.info(f'Username: {current_user} -- Response for POST "/daily_alarm": 401 {response}')
        return response, 401

@api.route('/once_alarm')
class OnceAlarmResource(Resource):
    @jwt_required(optional=True)
    @api.doc('once alarm mode', params={'percent':'openess', 'specify_time':'time to alarm'})
    @api.expect(once_alarm_model)
    @api.response(201, 'Success', alarm_responses_model)
    @api.response(400, 'Wrong date format', error_model)
    @api.response(401, 'User is not log in', error_model)
    @api.response(501, 'Esp32 disconnect to broker', error_model)
    def post(self):
        ''''Once alarm mode curtain'''
        current_user = get_jwt_identity()
        if current_user:
            data = request.get_json()
            logger_api.info(f'Username: {current_user} -- POST "/once_alarm" with payload {data}')
            global esp32_status

            if esp32_status:
                try:
                    job_id=create_once_alarm(current_user, data['percent'],data['specify_time'])

                except Exception as e:
                    response = {'error': "Wrong date format"}
                    logger_api.info(f'Username: {current_user} -- Response for POST "/once_alarm": 400 {response}')
                    return response, 400
                
                response = {'status': "true", 'job_id': job_id}
                logger_api.info(f'Username: {current_user} -- Response for POST "/once_alarm": 201 {response}')
                return response, 201

            response = {'error': "Esp32 disconnect to broker!"}
            logger_api.info(f'Username: {current_user} -- Response for POST "/once_alarm": 501 {response}')
            return response, 501
        else:
            response = {"error": "User is not logged in"}
            logger_api.info(f'Username: {current_user} -- Response for POST "/once_alarm": 401 {response}')
            return response, 401

def delete_job(username, job_id, collections):
    alarm_info = collections.find_one({"job_id": job_id, "username": username})
    if alarm_info:
        # Báo thức được tìm thấy, tiến hành xóa job và tài liệu trong MongoDB
        scheduler.remove_job(job_id)
        collections.delete_one({"job_id": job_id})
        return True
    return False

@app.route('/cancel_alarm')
class CancelAlarmResource(Resource):
    @jwt_required(optional=True)
    @api.doc('cancel alarm mode', params={'type':'type of alarm', 'job_id':'job_id'})
    @api.expect(once_alarm_model)
    @api.response(201, 'Success', result_model)
    @api.response(401, 'User is not log in', error_model)
    @api.response(404, 'Not found job', error_model)
    @api.response(501, 'Esp32 disconnect to broker', error_model)
    def delete(self):
        ''''Cancel alarm mode curtain'''
        current_user = get_jwt_identity()
        if current_user:
            data = request.get_json()
            logger_api.info(f'Username: {current_user} -- POST "/cancel_alarm" with payload {data}')
            global esp32_status

            if esp32_status:
                result = None
                if data['type'] == 'daily':
                    global daily_alarm_collections
                    result = delete_job(current_user, data['job_id'], daily_alarm_collections)

                if data['type'] == 'daily':
                    global once_alarm_collections
                    result = delete_job(current_user, data['job_id'], once_alarm_collections)
                
                if result:
                    response = {'status': "true"}
                    logger_api.info(f'Username: {current_user} -- Response for POST "/cancel_alarm": 201 {response}')
                    return response, 201
                
                response = {'error': "Not found job!"}
                logger_api.info(f'Username: {current_user} -- Response for POST "/cancel_alarm": 404 {response}')
                return response, 404
            
            response = {'error': "Esp32 disconnect to broker!"}
            logger_api.info(f'Username: {current_user} -- Response for POST "/cancel_alarm": 501 {response}')
            return response, 501
        
        response = {"error": "User is not logged in"}
        logger_api.info(f'Username: {current_user} -- Response for POST "/cancel_alarm": 401 {response}')
        return response, 401

#  -----------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=False)
