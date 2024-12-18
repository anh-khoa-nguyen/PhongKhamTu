from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from urllib.parse import quote  # Do mật khẩu DB có ký tự đặc biệt


app = Flask(__name__) # Tất cả cấu hình của dự án nằm trong đây
app.secret_key = 'SDASDEW!21321321s2'

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/clinicdb?charset=utf8mb4" % quote('Abc@123')
# TB1: Driver CSDL kết nối ;; TB2: Un,pass CSDL mình kết nối ;; TB3: Server chạy DB ;; TB4: Tên DB ;; TB5: Cờ tương tác tiếng việt dễ dàng
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SO_PHAN_TU"] = 10  # Thông số cấu hình số sản phẩm 1 trang (8)

db = SQLAlchemy(app)
login = LoginManager(app)  # Nguyên tắc của login cần phải có 1 cái hàm bên index.py