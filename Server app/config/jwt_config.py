import os

# Lấy đường dẫn thư mục của file broker_config.py
config_folder = os.path.dirname(os.path.abspath(__file__))

# Tạo đường dẫn tuyệt đối cho isgrootx1.pem và server.key
certificate_folder = os.path.join(config_folder, 'certificate')
server_key_path = os.path.join(certificate_folder, 'server.key')
class JwtConfig:
    JWT_SECRET_KEY = server_key_path