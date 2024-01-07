from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required, create_access_token, set_access_cookies, unset_jwt_cookies
from config.jwt_config import JwtConfig
from flask import request
from flask_restx import Api, Resource
from swagger import account_model, result_model, error_model
from logger import logger_api
from db import users_collection
from app import app

app.config.from_object(JwtConfig)
jwt = JWTManager(app)

api = Api(app, title='Bạn Hoàng rất đẹp trai!', version='1.0', description='API for controlling smart curtain')
from werkzeug.security import check_password_hash
from flask import jsonify, make_response

# Khi user đăng xuất, xóa token khỏi cookie của họ đồng thời thêm nó vào blasklist để tránh tấn công phát lại
blacklist = set()
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist

# Khi client login, trả về trạng thái đăng nhập thành công hay thất bại. Nếu đăng nhập thành công sẽ set token vào cookie của họ
@api.route('/login')
class LoginResource(Resource):
    @api.doc('Login')
    @api.expect(account_model)
    @api.response(200, 'Success', result_model)
    @api.response(401, 'Faied', error_model)
    def post(self):
        ''''Login account'''
        username = request.json.get('username')
        password = request.json.get('password')

        user = users_collection.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            logger_api.info(f"Username: {username} -- is logging in!")

            # Tạo access token và refresh token
            access_token = create_access_token(identity=username)
            print(f"Access token: {access_token}")

            # Thiết lập cookies cho access token và refresh token trực tiếp trên response
            response = make_response(jsonify({"status": True, "access_token": access_token}), 200)
            set_access_cookies(response, access_token)

            logger_api.info(f'Username: {username} -- logged in successfully!')
            return response
        
        logger_api.info(f'Username: {username} -- logged in failed!')
        return {'error': 'Bad username and password'}, 401

# Khi clien logout, trả về trạng thái thành công hay thất bại. Nếu logout thành công, xóa token khỏi cookie đồng thời thêm nó vào blacklist
@api.route('/logout')
class LogoutResource(Resource):
    @jwt_required(optional=True)
    @api.doc('Logout')
    @api.response(200, 'Success', result_model)
    @api.response(401, 'Failed', error_model)
    def post(self):
        ''''Logout account'''
        current_user = get_jwt_identity()
        
        if current_user:
            logger_api.info(f"Username: {current_user} -- is logging out!")

            # Thu hồi token
            jti = current_user.get('jti')  # Sử dụng get để tránh lỗi nếu 'jti' không tồn tại
            if jti:
                blacklist.add(jti)  # Thêm token vào danh sách đen khi đăng xuất
    
            # Xóa cookie liên quan đến jwt
            unset_jwt_cookies(response)
            response = jsonify({'status': True}, 200)

            logger_api.info(f'Username: {current_user} -- Successfully logged out!')
            return response
        else:
            logger_api.info(f'Username: {current_user} -- is not logged in!')
            return {"error": "User is not logged in"}, 401

from werkzeug.security import generate_password_hash

@api.route('/register')
class RegisterResource(Resource):
    @api.doc('Register')
    @api.expect(account_model)
    @api.response(201, 'Success', result_model)
    @api.response(401, 'Failed', error_model)
    def post(self):
        '''Register account'''
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        logger_api.info(f'Creating account for username: {username}.')

        # Kiểm tra xem tên người dùng đã tồn tại chưa
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            logger_api.info(f'Failed to register account for username: {username} -- username already exists.')
            return {"error": "Username already exists"}, 400

        # Hash mật khẩu trước khi lưu vào database
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Đăng ký người dùng mới
        new_user = {'username': username, 'password': hashed_password}
        users_collection.insert_one(new_user)

        response = {"status": "User registered successfully!"}

        logger_api.info(f'Successfully create account for username: {username}!')
        return response, 201

from apscheduler.schedulers.background import BackgroundScheduler
import datetime

# Hàm xóa token đã hết hạn khỏi danh sách đen
def clean_blacklist():
    now = datetime.utcnow()
    expired_tokens = {jti for jti, exp in blacklist if exp < now}
    blacklist.difference_update(expired_tokens)

# Thiết lập tiến trình định kỳ
scheduler = BackgroundScheduler(timezone='Asia/Ho_Chi_Minh')
scheduler.add_job(clean_blacklist, 'interval', minutes=30)  # Cập nhật mỗi 30 phút
scheduler.start()
