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