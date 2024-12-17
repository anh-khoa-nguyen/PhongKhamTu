from app.models import User, UserRole
from flask_admin import Admin, BaseView, expose #View bình thường gọi là BaseView
from app import app, db #Chèn db để thêm xóa sửa db
from flask_admin.contrib.sqla import ModelView #Quản trị thằng nào đó thì import thằng đó vào, Model-View gắn liền với 1 view - 1 model,
from flask_login import current_user, logout_user #Biến này ngoài View thì sài thoải mái nhưng trong phương thức thì phải import
from flask import redirect #Redirect về trang chủ quản trị sau khi đã Logout

admin = Admin(app=app, name='Phòng Khám Tư', template_mode='bootstrap4') #Đầu tiên luôn chèn cái app vào cho nó, tiếp theo là cái tên Website,

#Cài thư viện nó trong .venv --> Lib

class AdminView(ModelView):
    def is_accessible(self): #Được phép truy cập nếu như, còn không thì ẩn
        return current_user.is_authenticated and current_user.vaitro.__eq__(UserRole.ADMIN)


class UserView(AdminView):
        column_list = ['id', 'ten', 'username', 'password']


admin.add_view(UserView(User, db.session)) #Muốn chèn được dữ liệu phải có cái session xử lý chèn dữ liệu
