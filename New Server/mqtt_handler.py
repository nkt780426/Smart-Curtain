from config.broker_config import BrokerConfig
from flask_mqtt import Mqtt
from app import app, socketio, inform_collection
from logger import logger_broker
import json

mqtt = Mqtt(app)
app.config.from_object(BrokerConfig)

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