from pymongo import MongoClient
from config.database_config import DatabaseConfig


client = MongoClient(DatabaseConfig.DATABASE_URI)
db = client['smart_curtain']
inform_collection = db['inform']
users_collection = db['users']
daily_alarm_collections = db['daily_alarm']
once_alarm_collections = db['once_alarm_collections']