import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Enum, DateTime  # Tạo các trường, Enum này của CSDL
from sqlalchemy.orm import relationship # Tạo các mối quan hệ
from PhongKhamTu.app import db, app # import cái biến db, app bên file __init__ từ gói "app"
from enum import Enum as RoleEnum #Enum của Python, do trùng tên với Enum bên trên nên đặt lại là "RoleEnum"
from flask_login import UserMixin #Để sử dụng các chứng thực, lưu trạng thái đăng nhập có sẵn, ta phải kế thừa lớp User, "Mixin" là thứ làm sẵn mọi thứ, chỉ áp dụng sài thôi

class UserRole(RoleEnum): #Chỉ là định nghĩa enum.
    ADMIN = 1
    BACSI = 2
    YTA = 3

class User(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(50))  # Không trùng lắp giữa các thể hiện
    ngaythamgia = Column(DateTime, default=datetime.datetime.now())
    email = Column(String(50))
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg')
    vai_tro = Column(Enum(UserRole))

if __name__ == '__main__':  # Tự phát hiện cái bảng này chưa có và nó tạo ra
    with app.app_context():  # Trong phiên bản mới bắt lệnh này chạy trong ngữ cảnh ứng dụng
        db.create_all()  # Biến tất cả thành bảng dữ liệu, chuyển chữ "C" thành chữ "c"

        import hashlib  # Sử dụng thuật toán băm

        u = User(ten='admin', username='admin', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
                 # Encode phòng trường hợp mật khẩu có dấu TV, ép toàn bộ thành chụỗi
                 ,vai_tro=UserRole.ADMIN)

        u1 = User(ten='Bác sĩ An', username='bsan', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
                 # Encode phòng trường hợp mật khẩu có dấu TV, ép toàn bộ thành chụỗi
                 ,vai_tro=UserRole.BACSI, email="bsan@gmail.com")
        # db.session.add(u1)
        db.session.add_all([u, u1])
        db.session.commit()