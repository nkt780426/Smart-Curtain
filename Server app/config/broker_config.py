from datetime import timedelta
from decouple import config
import ssl, os

# Lấy đường dẫn thư mục của file broker_config.py
config_folder = os.path.dirname(os.path.abspath(__file__))

# Tạo đường dẫn tuyệt đối cho isgrootx1.pem và server.key
certificate_folder = os.path.join(config_folder, 'certificate')
isgrootx1_path = os.path.join(certificate_folder, 'isrgrootx1.pem')
server_key_path = os.path.join(certificate_folder, 'server.key')

class BrokerConfig:

    # Nạp các thuộc tính từ file .env
    MQTT_BROKER_URL = config('MQTT_BROKER_URL', default='')
    MQTT_BROKER_PORT = config('MQTT_BROKER_PORT', default=8883, cast=int)
    MQTT_USERNAME = config('MQTT_USERNAME', default='')
    MQTT_PASSWORD = config('MQTT_PASSWORD', default='')
    MQTT_KEEPALIVE = config('MQTT_KEEPALIVE', default=60, cast = int)

    # Các thuộc tính mặc định
    MQTT_TLS_ENABLED = True
    MQTT_TLS_CA_CERTS = isgrootx1_path
    MQTT_TLS_VERSION = ssl.PROTOCOL_TLSv1_2
    MQTT_TLS_CIPHERS = None
    MQTT_TLS_KEYFILE = server_key_path