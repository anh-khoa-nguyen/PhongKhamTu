import hashlib
import math
import pdb
from datetime import datetime

from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_admin.form import Select2Widget
from wtforms.fields.choices import SelectField

from app.models import User, UserRole, Thuoc, LoaiThuoc, HoaDon, ChuyenNganh, DonViThuoc, ThuocThuocLoai, \
    BenhNhan
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
    page_size = 10
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
        # Truy vấn tất cả bệnh nhân từ cơ sở dữ liệu
        current_time = datetime.now().strftime("%H:%M:%S, %d/%m/%Y")
        patients = BenhNhan.query.all()
        drugs = Thuoc.query.all()
        drugs = db.session.query(
            Thuoc.id,
            Thuoc.ten.label('name'),  # Tên thuốc
            Thuoc.gia.label('price'),  # Giá thuốc
            DonViThuoc.donvi.label('unit'),  # Đơn vị tính thuốc
            ThuocThuocLoai.tonkho.label('stock')  # Số lượng tồn kho
        ).join(
            DonViThuoc, Thuoc.donvithuoc_id == DonViThuoc.id
        ).join(
            ThuocThuocLoai, Thuoc.id == ThuocThuocLoai.thuoc_id
        ).all()

        return self.render('admin/lapphieukham.html', patients=patients, drugs=drugs, current_time=current_time)



admin.add_view(LPKView(name='Lập phiếu khám'))

#View của Y tá:
class LDSKView(YTView):
    @expose('/')
    def index(self):
        sobnmax = dao.load_sobntoida()
        ngayhientai = datetime.now().strftime('%Y-%m-%d')
        return self.render('admin/danhsachkham.html', sobntoida = sobnmax, ngayhientai = ngayhientai)
admin.add_view(LDSKView(name='Lập danh sách khám'))

#View của Thu ngân:
class TTHDView(TNView):
    @expose('/', methods=['get', 'post'])
    def index(self):

        page = request.args.get('page', 1)  # Lấy page ra, mặc định không gửi lấy số 1
        so_phan_tu = app.config['SO_PHAN_TU']
        total = dao.count_so_phan_tu(HoaDon)
        hds = dao.load_hoadon(int(page))

        # import pdb
        # pdb.set_trace()

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
            'choices': [(True, 'Nữ'), (False, 'Nam')], # giá trị chuỗi `'True'` hoặc `'False'`
            'coerce': lambda x: x in ["True", True], # Ép kiểu giá trị thành boolean
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
        if form.password.data:  # 'password' cần khớp với tên trường password trong form
            model.password =hashlib.md5(form.password.data.encode('utf-8')).hexdigest()
        super().on_model_change(form, model, is_created)

class QLThuocView(AdminView):
    edit_modal = True
    create_modal = True
    column_list = ['ten', 'tac_dung', 'gia', 'donvithuoc.donvi', 'tonkho', 'loaithuocs']
    column_searchable_list = ['ten']
    column_labels = {
        'ten': 'Tên',
        'tac_dung': 'Tác dụng',
        'gia': 'Giá',
        'tonkho': 'Tồn kho',
        'donvithuoc.donvi': 'Đơn vị thuốc',
        'loaithuocs': 'Loại thuốc'
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
    form_excluded_columns = ['chitietphieukhams']

    def on_model_change(self, form, model, is_created):
        if form.donvithuoc.data:
            model.donvithuoc_id = form.donvithuoc.data.id
        super().on_model_change(form, model, is_created)

    def on_model_change(self, form, model, is_created):
        if form.donvithuoc.data:
            model.donvithuoc_id = form.donvithuoc.data.id
        super().on_model_change(form, model, is_created)

    def on_model_change(self, form, model, is_created):
        if form.donvithuoc.data:
            model.donvithuoc_id = form.donvithuoc.data.id
        super().on_model_change(form, model, is_created)

class QLLoaiThuocView(AdminView):
    edit_modal = True
    create_modal = True
    column_searchable_list = ['ten']
    column_list = ['ten']
    column_labels = {
        'ten': 'Tên Loại Thuốc'
    }

    # Loại bỏ trường "thuoc" khỏi form
    form_excluded_columns = ['thuoc']

    def on_model_change(self, form, model, is_created):
        # Xử lý các logic khác khi lưu dữ liệu, nếu cần
        super().on_model_change(form, model, is_created)

class QuyDinhView(AdminView):
    pass

class SoBenhNhanView(BaseView):
    @expose('/', methods=['get', 'put'])
    def index(self):
        if request.method.__eq__('PUT'):
            try:
                new_max = int(request.form.get('maxPatients'))
                new_quality = int(request.form.get('price'))
                if new_max < 1:
                    return jsonify({"success": False, "message": "Giá trị phải lớn hơn 0!"}), 400

                if new_quality < 1:
                    return jsonify({"success": False, "message": "Giá trị phải lớn hơn 0!"}), 400
                # app.config['SO_TIEN_KHAM'] = new_quality

                return jsonify({"success": True, "message": "Cập nhật thành công!"}), 200
            except Exception as e:
                return jsonify({"success": False, "message": "Có lỗi xảy ra: " + str(e)}), 500

        sobnmax = dao.load_sobntoida()
        sotienkham = dao.load_sotienkham()
        return self.render('admin/bntoida.html', sobntoida = sobnmax, sotienkham = f"{sotienkham:,}")

    def is_accessible(self):
        return current_user.is_authenticated and current_user.vaitro == UserRole.ADMIN

admin.add_view(SoBenhNhanView(name='Số bệnh nhân tối đa'))

class ThongKeView(BaseView):
    @expose('/')
    def index(self):
        monthmedicine = request.args.get('monthMedicine', datetime.now().month)
        yearmedicine = request.args.get('yearMedicine', datetime.now().year)
        month = request.args.get('month', datetime.now().month)
        year =  request.args.get('year', datetime.now().year)
        monthstats = request.args.get('monthstats', datetime.now().month)
        yearstats =  request.args.get('yearstats', datetime.now().year)
        doanhthu = dao.doanhthu(monthstats, yearstats)
        tongdoanhthu = sum(item[2] for item in doanhthu if item[2])
        return self.render('/admin/thongke.html',medicine_stats=dao.medicine_rates_month_stats(monthmedicine,yearmedicine), tansuatkhamtheothang=dao.tansuatkham(month,year), doanhthu = doanhthu,tongdoanhthu= tongdoanhthu,monthmedicine=monthmedicine,yearmedicine=yearmedicine,
                           month=month,
                           year=year,
                           monthstats=monthstats,
                           yearstats=yearstats)

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
admin.add_view(LogoutView(name='Đăng xuất'))
