from flask_restx import Api, fields
from app import app

api = Api(app, title='Bạn Hoàng rất đẹp trai!', version='1.0', description='API for controlling smart curtain')

# Tạo model để validate dữ liệu trả về (Swagger)
result_model = api.model('result',{
    'status': fields.Boolean(required=True)
})

alarm_responses_model = api.model('alarm_responses',{
    'type': fields.String(required=True),
    'job_id': fields.String(required=True)
})

error_model = api.model('error',{
    'error': fields.String(required=True)
})

account_model = api.model('account',{
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

auto_model = api.model('auto',{
    'status': fields.Boolean(required=True),
    'percent': fields.Integer(required=True)
})

daily_alarm_model = api.model('daily_alarm',{
    'percent': fields.Float(required=True, description='openess'),
    'hours': fields.Integer(required=True, description='hours'),
    'minutes': fields.Integer(required=True, description='minutes')
})

once_alarm_model = api.model('once_alarm',{
    'percent': fields.Float(required=True, description='openess'),
    'specify_time': fields.String(required=True, description='Time to alarm')
})

cancel_alarm_model = api.model('cancel_alarm',{
    'type': fields.String(required=True),
    'job_id': fields.String(required=True)
})

status_model = api.model('status',{
    'auto': fields.Nested(auto_model),
    'daily_alarm': fields.List(fields.Nested(daily_alarm_model)),
    'once_alarm': fields.List(fields.Nested(once_alarm_model))
})
