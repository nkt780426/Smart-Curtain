from decouple import config

class DatabaseConfig:
    DATABASE_URI = config('DATABASE_URI', default = '')