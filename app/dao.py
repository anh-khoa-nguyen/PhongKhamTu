from app.models import User #Dùng DL trong bảng dữ liệu
from app import app, db #Import để lấy các thông số cấu hình, db để thêm vào CSDL
import hashlib

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password))

    return u.first()

def get_user_by_id(user_id):
    return User.query.get(user_id) #Truy vấn trong bảng dữ liệu để lấy user_id