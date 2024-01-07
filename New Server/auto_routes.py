from flask import request
from threading import Thread, Event
from swagger import api, auto_model,result_model, error_model
from flask_restx import Resource
from logger import logger_api, logger_broker
from login import jwt_required, get_jwt_identity
from mqtt_handler import mqtt, esp32_status, auto_responses

import time
import uuid
import json

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