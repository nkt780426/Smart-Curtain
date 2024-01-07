from logger import logger_broker
from threading import Thread,Event
from login import scheduler, api, jwt_required, daily_alarm_model, alarm_responses_model, error_model, get_jwt_identity, cancel_alarm_model, result_model
from flask_restx import Resource
from logger import logger_api
import uuid, time, datetime


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

@api.route('/cancel_alarm')
class CancelAlarmResource(Resource):
    @jwt_required(optional=True)
    @api.doc('cancel alarm mode', params={'type':'type of alarm', 'job_id':'job_id'})
    @api.expect(cancel_alarm_model)
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