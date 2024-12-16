import math
from datetime import datetime

from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_admin.form import Select2Widget
from wtforms.fields.choices import SelectField

from app.models import User, UserRole, Thuoc, LoaiThuoc, DichVu, HoaDon, ChuyenNganh, DonViThuoc
from flask_admin import Admin, BaseView, expose #View bình thường gọi là BaseView
from app import app, db #Chèn db để thêm xóa sửa db
from flask_admin.contrib.sqla import ModelView #Quản trị thằng nào đó thì import thằng đó vào, Model-View gắn liền với 1 view - 1 model,
from flask_login import current_user, logout_user #Biến này ngoài View thì sài thoải mái nhưng trong phương thức thì phải import
from flask import request, redirect, jsonify #Redirect về trang chủ quản trị sau khi đã Logout

import dao
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
class LDSKView(YTView):
    @expose('/')
    def index(self):
        sobnmax = dao.load_sobntoida()
        return self.render('admin/danhsachkham.html', sobntoida = sobnmax)
admin.add_view(LDSKView(name='Lập danh sách khám'))

#View của Thu ngân:
class TTHDView(TNView):
    @expose('/', methods=['get', 'post'])
    def index(self):

        page = request.args.get('page', 1)  # Lấy page ra, mặc định không gửi lấy số 1
        so_phan_tu = app.config['SO_PHAN_TU']
        total = dao.count_so_phan_tu(HoaDon)
        hds = dao.load_hoadon(int(page))

        return self.render('admin/hoadon.html', hoadons = hds, pages = math.ceil(total/so_phan_tu))
admin.add_view(TTHDView(name='Thanh toán hóa đơn'))

#View của Admin:
class UserView(AdminView):
    column_list = ['username', 'ten', 'ngaysinh', 'gioitinh', 'chuyennganh.ten', 'vaitro', 'sdt']
    edit_modal = True
    create_modal = True
    column_formatters = {
        'gioitinh': lambda v, c, m, p: 'Nữ' if m.gioitinh else 'Nam'
    }
    form_overrides = {
        'gioitinh': SelectField
    }

    form_args = {
        'gioitinh': {
            'choices': [(True, 'Nữ'), (False, 'Nam')],
            'label': 'Giới Tính'
        }
    }
    column_searchable_list = ['ten']
    column_labels = {
        'username': 'Username',
        'ten': 'Họ tên',
        'ngaysinh': 'Ngày sinh',
        'gioitinh': 'Giới tính',
        'chuyennganh.ten': 'Tên Chuyên Ngành',
        'vaitro': 'Quyền',
        'sdt': 'Số điện thoại'
    }
    form_extra_fields = {
        'chuyennganh': QuerySelectField(
            'Chuyên Ngành',
            query_factory=lambda: db.session.query(ChuyenNganh).all(),
            get_label='ten',  # Lấy tên chuyên ngành hiển thị
            allow_blank=False,  # Không cho phép giá trị rỗng
            widget=Select2Widget()
        )
    }

    def on_model_change(self, form, model, is_created):
        if form.chuyennganh.data:
            model.chuyennganh_id = form.chuyennganh.data.id
        super().on_model_change(form, model, is_created)


class QLThuocView(AdminView):
    column_list = ['ten','tac_dung','gia','donvithuoc.donvi','loaithuocs']
    column_labels = {
        'ten': 'Tên',
        'tac_dung':'Tác dụng',
        'gia': 'Giá',
        'donvithuoc.donvi': 'Đơn vị thuốc',
        'loaithuocs':'Loại thuốc'
    }
    form_extra_fields = {
        'donvithuoc': QuerySelectField(
            'Đơn vị Thuốc',
            query_factory=lambda: db.session.query(DonViThuoc).all(),
            get_label='donvi',  # Lấy tên  hiển thị
            allow_blank=False,  # Không cho phép giá trị rỗng
            widget=Select2Widget()
        )
    }

    def on_model_change(self, form, model, is_created):
        if form.donvithuoc.data:
            model.donvithuoc_id = form.donvithuoc.data.id
        super().on_model_change(form, model, is_created)

class QLLoaiThuocView(AdminView):
    pass

class QuyDinhView(AdminView):
    pass

class SoBenhNhanView(BaseView):
    @expose('/', methods=['get', 'put'])
    def index(self):
        if request.method.__eq__('PUT'):
            try:
                new_max = int(request.form.get('maxPatients'))
                if new_max < 1:
                    return jsonify({"success": False, "message": "Giá trị phải lớn hơn 0!"}), 400

                app.config['SO_BENH_NHAN_TRONG_NGAY'] = new_max

                return jsonify({"success": True, "message": "Cập nhật thành công!"}), 200
            except Exception as e:
                return jsonify({"success": False, "message": "Có lỗi xảy ra: " + str(e)}), 500

        sobnmax = dao.load_sobntoida()
        return self.render('admin/bntoida.html', sobntoida = sobnmax)
    def is_accessible(self):
        return current_user.is_authenticated and current_user.vaitro == UserRole.ADMIN

admin.add_view(SoBenhNhanView(name='Số bệnh nhân tối đa'))

class ThongKeView(BaseView):
    @expose('/')
    def index(self):
        monthmedicine = request.args.get('monthMedicine', datetime.now().month)
        month = request.args.get('month', datetime.now().month)
        return self.render('/admin/thongke.html',medicine_stats=dao.medicine_rates_month_stats(monthmedicine), tansuatkhamtheothang=dao.tansuatkham(month))

    # , profit_stats = utils.profit_month_stats(month), total_month_profit = utils.total_profit_mont(month),

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


admin.add_view(UserView(User, db.session, name='Người dùng')) #Muốn chèn được dữ liệu phải có cái session xử lý chèn dữ liệu
admin.add_view(QLThuocView(Thuoc,db.session, name='Thuốc'))
admin.add_view(QLLoaiThuocView(LoaiThuoc,db.session,name='Loại thuốc'))
admin.add_view(QuyDinhView(DichVu, db.session, name='Dịch vụ'))
admin.add_view(LogoutView(name='Đăng xuất'))
