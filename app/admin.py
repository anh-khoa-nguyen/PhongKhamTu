from app.models import User, UserRole, Thuoc, LoaiThuoc, DichVu
from flask_admin import Admin, BaseView, expose #View bình thường gọi là BaseView
from app import app, db #Chèn db để thêm xóa sửa db
from flask_admin.contrib.sqla import ModelView #Quản trị thằng nào đó thì import thằng đó vào, Model-View gắn liền với 1 view - 1 model,
from flask_login import current_user, logout_user #Biến này ngoài View thì sài thoải mái nhưng trong phương thức thì phải import
from flask import redirect #Redirect về trang chủ quản trị sau khi đã Logout

admin = Admin(app=app, name='Phòng Khám Tư', template_mode='bootstrap4') #Đầu tiên luôn chèn cái app vào cho nó, tiếp theo là cái tên Website,
#Cài thư viện nó trong .venv --> Lib

#Giới hạn quyền theo UserRole:
class AdminView(ModelView):
    def is_accessible(self): #Được phép truy cập nếu như, còn không thì ẩn
        return current_user.is_authenticated and current_user.vaitro == UserRole.ADMIN

class BSView(BaseView):
    def is_accessible(self):  # Được phép truy cập nếu như, còn không thì ẩn
        return current_user.is_authenticated and current_user.vaitro == UserRole.BACSI

class YTView(BaseView):
    def is_accessible(self):  # Được phép truy cập nếu như, còn không thì ẩn
        return current_user.is_authenticated and current_user.vaitro == UserRole.YTA

class TNView(BaseView):
    def is_accessible(self):  # Được phép truy cập nếu như, còn không thì ẩn
        return current_user.is_authenticated and current_user.vaitro == UserRole.THUNGAN

#View của Bác sĩ:
class LPKView(BSView):
    @expose('/')
    def index(self):
        return self.render('admin/lapphieukham.html')
admin.add_view(LPKView(name='Lập phiếu khám'))

#View của Y tá:
class LDSKView(BSView):
    @expose('/')
    def index(self):
        return self.render('admin/danhsachkham.html')
admin.add_view(LDSKView(name='Lập danh sách khám'))

#View của Thu ngân:
class TTHDView(TNView):
    @expose('/')
    def index(self):
        return self.render('admin/hoadon.html')
admin.add_view(TTHDView(name='Thanh toán hóa đơn'))

#View của Admin:
class UserView(AdminView):
        column_list = ['id', 'ten', 'username', 'password']

class QLThuocView(AdminView):
    pass

class QLLoaiThuocView(AdminView):
    pass

class QuyDinhView(AdminView):
    pass

class ThongKeView(BaseView):
    @expose('/')

    def index(self):
        logout_user()
        return redirect('/')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.vaitro == UserRole.ADMIN

admin.add_view(ThongKeView(name='Thống kê'))

#View chung:
class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/')
    def is_accessible(self):
        return current_user.is_authenticated
admin.add_view(LogoutView(name='Đăng xuất'))

admin.add_view(UserView(User, db.session)) #Muốn chèn được dữ liệu phải có cái session xử lý chèn dữ liệu
admin.add_view(QLThuocView(Thuoc,db.session))
admin.add_view(QLLoaiThuocView(LoaiThuoc,db.session))
admin.add_view(QuyDinhView(DichVu, db.session))
