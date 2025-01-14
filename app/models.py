import datetime
from datetime import date

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Enum, DateTime, \
    Double, Date  # Tạo các trường, Enum này của CSDL
from sqlalchemy.orm import relationship  # Tạo các mối quan hệ
from app import db, app  # import cái biến db, app bên file __init__ từ gói "app"
from enum import Enum as RoleEnum  # Enum của Python, do trùng tên với Enum bên trên nên đặt lại là "RoleEnum"
from flask_login import \
    UserMixin  # Để sử dụng các chứng thực, lưu trạng thái đăng nhập có sẵn, ta phải kế thừa lớp User, "Mixin" là thứ làm sẵn mọi thứ, chỉ áp dụng sài thôi


# Liên quan đến người dùng
class UserRole(RoleEnum):  # Chỉ là định nghĩa enum.
    ADMIN = 1
    BACSI = 2
    YTA = 3
    THUNGAN = 4


class ChuyenNganh(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(50))
    isKham = Column(Boolean, default=False)
    users = relationship('User', backref='chuyennganh',
                         lazy=True)
    def __str__(self):
        return self.ten

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(50))  # Không trùng lắp giữa các thể hiện
    ngaysinh = Column(Date)
    gioitinh = Column(Boolean)
    ngaythamgia = Column(DateTime, default=datetime.datetime.now())
    email = Column(String(50), unique=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg')
    sdt = Column(String(10), nullable=False, unique=True)
    chuyennganh_id = Column(Integer, ForeignKey(ChuyenNganh.id), nullable=False)
    vaitro = Column(Enum(UserRole))
    danhsachkhams = relationship('DanhSachKham', backref='user',
                                 lazy=True)
    phieukhambenhs = relationship('PhieuKhamBenh', backref='user',
                                  lazy=True)
    hoadons = relationship('HoaDon', backref='user',
                           lazy=True)
    lichkhams = relationship('LichKham', backref='user',
                             lazy=True)
    phieudatlichs = relationship('PhieuDatLich', backref='user', lazy=True)

    def __init__(self, ten, username, password, vaitro, sdt=None, ngaysinh=None, chuyennganh_id=None, email=None,
                 gioitinh=None):
        self.ten = ten
        self.username = username
        self.password = password
        self.vaitro = vaitro
        self.sdt = sdt
        self.ngaysinh = date.fromisoformat(ngaysinh) if ngaysinh else None  # Chuyển đổi từ chuỗi sang kiểu date
        self.chuyennganh_id = chuyennganh_id
        self.email = email
        self.gioitinh = gioitinh \
 \

            # Liên quan đến quá trình khám bệnh:


class LoaiBenh(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(50))


class BenhNhan(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(50))  # Không trùng lắp giữa các thể hiện
    ngaysinh = Column(Date, default='2000-01-01')
    gioitinh = Column(Boolean)
    sdt = Column(String(10), nullable=False, unique=True)
    email = Column(String(50))
    phieukhambenhs = relationship('PhieuKhamBenh', backref='benhnhan',
                                  lazy=True)
    phieudatlichs = relationship('PhieuDatLich', backref='benhnhan', lazy=True)


class DanhSachKham(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ngaylap = Column(Date, default=datetime.datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=True)
    # lichkhams = relationship('LichKham', backref='danhsachkham',
    #                          lazy=True)
    # benhnhans = relationship('BenhNhan', secondary='ds_kham_co_benh_nhan', lazy='subquery',
    #                          backref=db.backref('danhsachkhams', lazy=True))

    phieudatlichs = relationship('PhieuDatLich', backref='danhsachkham', lazy=True)


class PhieuKhamBenh(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ngaykham = Column(DateTime, default=datetime.datetime.now())
    benhnhan_id = Column(Integer, ForeignKey(BenhNhan.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=True)
    hoadons = relationship('HoaDon', backref='phieukhambenh',
                           lazy=True)


class DonViThuoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    donvi = Column(String(20))
    thuocs = relationship('Thuoc', backref='donvithuoc',
                          lazy=True)

    def __str__(self):
        return self.donvi


class Thuoc(db.Model):

    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(50))
    tac_dung = Column(String(150))
    gia = Column(Double)
    tonkho = Column(Integer)
    donvithuoc_id = Column(Integer, ForeignKey(DonViThuoc.id), nullable=False)
    loaithuocs = db.relationship('LoaiThuoc', secondary="thuoc_thuoc_loai",
                                 backref=db.backref('thuoc', lazy='dynamic'))
    chitietphieukhams = relationship('ChiTietPhieuKham', backref='thuoc',
                                     lazy='dynamic')  # - mối quan hệ này không cần tải và xử lý ngay lập tức.

    def __str__(self):
        return self.ten

class LoaiThuoc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(20))

    def __str__(self):
        return self.ten


class ThuocThuocLoai(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    thuoc_id = Column(Integer, ForeignKey(Thuoc.id), nullable=False)
    loaithuoc_id = Column(Integer, ForeignKey(LoaiThuoc.id), nullable=False)


class ChiTietPhieuKham(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    soluongthuoc = Column(Integer)
    thuoc_id = Column(Integer, ForeignKey(Thuoc.id), nullable=True)
    phieukhambenh_id = Column(Integer, ForeignKey(PhieuKhamBenh.id), nullable=False)


class HoaDon(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    isThanhtoan = Column(Boolean)
    phieukhambenh_id = Column(Integer, ForeignKey(PhieuKhamBenh.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=True)
    ngaytao = Column(DateTime, default=datetime.datetime.now())
    # chitiethoadons = relationship('ChiTietHoaDon', backref='hoadon', lazy=True)
    gia_kham = db.Column(db.Integer, nullable=False, default=app.config['SO_TIEN_KHAM'])


# class ChiTietHoaDon(db.Model):
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     giathuoc = Column(Double)
#     giadichvu = Column(Double)
#     hoadon_id = Column(Integer, ForeignKey(HoaDon.id), nullable=False)


# class DSKhamCoBenhNhan(db.Model):
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     danhsachkham_id = Column(Integer, ForeignKey(DanhSachKham.id), nullable=False)
#     benhnhan_id = Column(Integer, ForeignKey(BenhNhan.id), nullable=False)


class PKBCoBenh(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    phieukhambenh_id = Column(Integer, ForeignKey(PhieuKhamBenh.id), nullable=False)
    loaibenh_id = Column(Integer, ForeignKey(LoaiBenh.id), nullable=False)


# Lịch khám

class KhungGio(db.Model):
    id = Column(Integer, primary_key=True)
    khoangthoigian = Column(String(20))
    lichkhams = relationship('LichKham', backref='khunggio',
                             lazy=True)

class LichKham(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=True)
    khunggio_id = Column(Integer, ForeignKey(KhungGio.id), nullable=False)
    ngay = Column(Date, default=datetime.datetime.now())
    isTrong = Column(Boolean)

class PhieuDatLich(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ngaydatlich = Column(DateTime, default=datetime.datetime.now())
    benhnhan_id = Column(Integer, ForeignKey(BenhNhan.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=True)
    trieuchung = Column(String(50))
    danhsachkham_id = Column(Integer, ForeignKey(DanhSachKham.id))

class BinhLuan(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten = Column(String(150), nullable=False)
    nghenghiep = Column(String(150), nullable=False)
    binhluan = Column(String(255), nullable=False)
    avatar = Column(String(100),
                    default='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg')
    star_value = Column(Integer)
    ngaytao = Column(DateTime, default=datetime.datetime.now())

if __name__ == '__main__':  # Tự phát hiện cái bảng này chưa có và nó tạo ra
    with app.app_context():  # Trong phiên bản mới bắt lệnh này chạy trong ngữ cảnh ứng dụng
        db.create_all()  # Biến tất cả thành bảng dữ liệu, chuyển chữ "C" thành chữ "c"
        db.session.commit()

        # Chuyên ngành:
        cn1 = ChuyenNganh(ten='Quản trị', isKham=False)
        cn2 = ChuyenNganh(ten='Thu Ngân', isKham=False)
        cn3 = ChuyenNganh(ten='Nhi đa khoa', isKham=True)
        cn4 = ChuyenNganh(ten='Ngoại lồng ngực', isKham=True)
        db.session.add_all([cn1, cn2, cn3, cn4])
        db.session.commit()

        # Người dùng
        import hashlib  # Sử dụng thuật toán băm

        u = User(ten='admin', username='admin', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
                 # Encode phòng trường hợp mật khẩu có dấu TV, ép toàn bộ thành chụỗi
                 , vaitro=UserRole.ADMIN, sdt='0123456777', ngaysinh='2001-12-05',
                 email="adminou@gmail.com", gioitinh=1, chuyennganh_id=1)

        u1 = User(ten='Bác sĩ An', username='bsan', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
                  # Encode phòng trường hợp mật khẩu có dấu TV, ép toàn bộ thành chụỗi
                  , vaitro=UserRole.BACSI, email="bsan@gmail.com", sdt='0123456781',
                  ngaysinh='2001-11-05', gioitinh=0, chuyennganh_id=3)

        u2 = User(ten='Y tá Dâu', username='ytadau', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
                  # Encode phòng trường hợp mật khẩu có dấu TV, ép toàn bộ thành chụỗi
                  , vaitro=UserRole.YTA, email="ytadau@gmail.com", sdt='0123456782',
                  ngaysinh='2001-10-05', gioitinh=1, chuyennganh_id=4)

        u3 = User(ten='Thu ngân OU', username='thunganou',
                  password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
                  # Encode phòng trường hợp mật khẩu có dấu TV, ép toàn bộ thành chụỗi
                  , vaitro=UserRole.THUNGAN, email="thunganou@gmail.com", sdt='0123456783',
                  ngaysinh='2001-09-05', gioitinh=0, chuyennganh_id=2)

        db.session.add_all([u, u1, u2, u3])
        db.session.commit()

        # Bệnh nhân:
        bn1 = BenhNhan(ten='Trần Quang Huy', ngaysinh='2001-12-05', gioitinh=0, sdt='0123456781', email='abc@123')
        bn2 = BenhNhan(ten='Phạm Huy Cảnh', ngaysinh='2001-06-29', gioitinh=1, sdt='0123456782', email='abc@123')
        bn3 = BenhNhan(ten='Lê Xuân Huy', ngaysinh='2002-11-15', gioitinh=0, sdt='0123456783', email='abc@123')
        db.session.add_all([bn1, bn2, bn3])
        db.session.commit()
        #
        # Loại bệnh:
        loaibenh1 = LoaiBenh(ten='Cảm')
        loaibenh2 = LoaiBenh(ten='Ho')
        loaibenh3 = LoaiBenh(ten='Xổ mũi')
        db.session.add_all([loaibenh1, loaibenh2, loaibenh3])
        db.session.commit()

        # Phiếu khám bệnh:
        pk1 = PhieuKhamBenh(benhnhan_id=1, user_id=2)
        pk2 = PhieuKhamBenh(benhnhan_id=2, user_id=2)
        pk3 = PhieuKhamBenh(benhnhan_id=3, user_id=2)
        db.session.add_all([pk1, pk2, pk3])
        db.session.commit()
        #
        # Phiếu khám bệnh có bệnh
        pkb1 = PKBCoBenh(phieukhambenh_id=1, loaibenh_id=2)
        pkb2 = PKBCoBenh(phieukhambenh_id=1, loaibenh_id=3)
        db.session.add_all([pkb1, pkb2])
        db.session.commit()

        # Hóa đơn
        hd1 = HoaDon(isThanhtoan=False, phieukhambenh_id=1, user_id=4)
        hd2 = HoaDon(isThanhtoan=True, phieukhambenh_id=2, user_id=4)
        hd3 = HoaDon(isThanhtoan=False, phieukhambenh_id=3, user_id=4)
        db.session.add_all([hd1, hd2, hd3])
        db.session.commit()




        #
        # Đơn vị thuốc
        dvt1 = DonViThuoc(donvi='Viên')
        dvt2 = DonViThuoc(donvi='Gram')
        dvt3 = DonViThuoc(donvi='Tube')
        dvt4 = DonViThuoc(donvi='Ống')
        dvt5 = DonViThuoc(donvi='Gói')
        dvt6 = DonViThuoc(donvi='Lọ')
        db.session.add_all([dvt1, dvt2, dvt3, dvt4, dvt5, dvt6])
        db.session.commit()

        # Thuốc
        t1 = Thuoc(ten='Xylocaine Jelly', tac_dung='Gây tê bôi trơn, giảm đau ngoài da', gia=55600, tonkho=3600,
                   donvithuoc_id=1)
        t2 = Thuoc(ten='Vintanil',
                   tac_dung='Điều trị cơn chóng mặt không rõ nguyên nhân, chóng mặt do kích thích, chóng mặt do ngộ độc thực phẩm, chóng mặt do tác dụng phụ của thuốc',
                   gia=11983, tonkho=6000, donvithuoc_id=3)
        t3 = Thuoc(ten='Vipredni 16mg', tac_dung='Chống viêm và ức chế hệ thống miễn dịch', gia=1890, tonkho=5500,
                   donvithuoc_id=2)
        db.session.add_all([t1, t2, t3])
        db.session.commit()

        # Loại thuốc
        lt1 = LoaiThuoc(ten='Acetyl leucin')
        lt2 = LoaiThuoc(ten='Methyl prednisolon')
        lt3 = LoaiThuoc(ten='Drotaverin clohydrat')
        db.session.add_all([lt1, lt2, lt3])
        db.session.commit()

        # Thuốc thuộc loại
        ttl1 = ThuocThuocLoai(thuoc_id=2, loaithuoc_id=3)
        ttl2 = ThuocThuocLoai(thuoc_id=1, loaithuoc_id=2)
        ttl3 = ThuocThuocLoai(thuoc_id=3, loaithuoc_id=1)
        db.session.add_all([ttl1, ttl2, ttl3])
        db.session.commit()

        # Chi tiết phiếu khám
        ctpk1 = ChiTietPhieuKham(soluongthuoc=23, thuoc_id=2, phieukhambenh_id=3)
        ctpk2 = ChiTietPhieuKham(soluongthuoc=2, thuoc_id=1, phieukhambenh_id=2)
        ctpk3 = ChiTietPhieuKham(soluongthuoc=7, thuoc_id=3, phieukhambenh_id=1)
        db.session.add_all([ctpk1, ctpk2, ctpk3])
        db.session.commit()

        # # Danh sách khám
        # danhsachkham1 = DanhSachKham(user_id=1)
        # danhsachkham2 = DanhSachKham(user_id=2)
        # danhsachkham3 = DanhSachKham(user_id=3)
        # db.session.add_all([danhsachkham1, danhsachkham2, danhsachkham3])
        # db.session.commit()

        # Khung giờ:
        kg1 = KhungGio(id=1, khoangthoigian='8h - 10h')
        kg2 = KhungGio(id=2, khoangthoigian='10h - 12h')
        kg3 = KhungGio(id=3, khoangthoigian='12h - 14h')
        kg4 = KhungGio(id=4, khoangthoigian='14h - 16h')
        kg5 = KhungGio(id=5, khoangthoigian='16h - 18h')
        db.session.add_all([kg1, kg2, kg3])
        db.session.commit()

        # Lịch khám
        lk1 = LichKham(user_id=2, khunggio_id=1, isTrong=True)
        lk2 = LichKham(user_id=2, khunggio_id=2, isTrong=True)
        lk3 = LichKham(user_id=2, khunggio_id=3, isTrong=True)

        lk4 = LichKham(user_id=2, khunggio_id=1, isTrong=True, ngay='2024-12-28')
        lk5 = LichKham(user_id=2, khunggio_id=2, isTrong=True, ngay='2024-12-29')
        lk6 = LichKham(user_id=2, khunggio_id=3, isTrong=True, ngay='2024-12-30')
        db.session.add_all([lk1, lk2, lk3, lk4, lk5, lk6])
        db.session.commit()

        # Các bình luận
        bl1 = BinhLuan(ten='Yến Hoàng', nghenghiep='Kế Toán', binhluan='bệnh viện sạch sẽ, dịch vụ nhanh chóng',
                       star_value=5)
        bl2 = BinhLuan(ten='Mi Hồ', nghenghiep='Bất động sản', binhluan='bệnh viện tốt, dịch vụ ổn', star_value=2)
        bl3 = BinhLuan(ten='Khoa Nguyễn', nghenghiep='Giáo viên tâm lý', binhluan='bệnh viện ok', star_value=3)
        db.session.add_all([bl1, bl2, bl3])
        db.session.commit()


        #Bổ sung
        u1 = User(ten='Bác sĩ Dương', username='bsduong', password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
                  # Encode phòng trường hợp mật khẩu có dấu TV, ép toàn bộ thành chụỗi
                  , vaitro=UserRole.BACSI, email="bsduong@gmail.com", sdt='0123456786',
                  ngaysinh='2001-11-05', gioitinh=0, chuyennganh_id=4)
        db.session.add(u1)
        db.session.commit()

        lk4 = LichKham(user_id=5, khunggio_id=1, isTrong=True, ngay='2024-12-27')
        lk5 = LichKham(user_id=5, khunggio_id=2, isTrong=True, ngay='2024-12-28')
        lk6 = LichKham(user_id=5, khunggio_id=3, isTrong=True, ngay='2024-12-29')
        db.session.add_all([lk4, lk5, lk6])
        db.session.commit()

# LichKham: Bác sĩ - giờ (đưa ra cố định) - Istrống ==> Đủ 40 hàng thì không khám nữa: Ngày: isTrong = False
#
# KhungGio: 1 - 8h - 10h
#           2 - 10h - 12h
#           3 - 12h - 14h
#           4 - 14h - 16h
#           5 - 16h - 18h

# A - 1 - True
# A - 2 - True
# A - 3 - True
# A - 4 - True
# A - 5 - True

# B - 1 - True
# B - 2 - True
# B - 3 - True
# B - 4 - True
# C - 5 - True

