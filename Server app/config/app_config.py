from decouple import config

class AppConfig:
    SECRET_CURTAIN_CODE = config('SECRET_CURTAIN_CODE', default = '123456789')