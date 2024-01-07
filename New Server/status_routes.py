from swagger import api, status_model, error_model
from logger import logger_api
from flask_restx import Resource
from login import jwt_required, get_jwt_identity
from mqtt_handler import esp32_status, auto_mode
from db import daily_alarm_collections, once_alarm_collections

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