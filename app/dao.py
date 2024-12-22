import datetime
from datetime import date

from app.models import User, HoaDon, PhieuKhamBenh, BenhNhan, ChuyenNganh, UserRole, LichKham, KhungGio  # Dùng DL trong bảng dữ liệu
from app.models import PhieuKhamBenh, ChiTietPhieuKham, Thuoc, DonViThuoc
from app import app, db  # Import để lấy các thông số cấu hình, db để thêm vào CSDL
import hashlib
from sqlalchemy import extract, func

def get_day(input_date=None):
    """
    Lấy tên ngày trong tuần từ một ngày nhất định (hoặc ngày hiện tại nếu không truyền tham số).
    Trả về tên ngày bằng tiếng Việt.

    :param input_date: Ngày (kiểu datetime.date). Mặc định là ngày hôm nay.
    :return: Tên ngày bằng tiếng Việt (str).
    """
    # Lấy ngày hiện tại hoặc ngày được cung cấp
    if input_date is None:
        input_date = datetime.date.today()

    # Ánh xạ tên ngày từ tiếng Anh sang tiếng Việt
    day_mapping = {
        "Monday": "2",
        "Tuesday": "3",
        "Wednesday": "4",
        "Thursday": "5",
        "Friday": "6",
        "Saturday": "7",
        "Sunday": "CN"
    }

    # Lấy tên ngày trong tuần (English)
    eng_day = input_date.strftime("%A")  # '%A' trả về tên ngày dài: Monday, Tuesday, ...

    # Dịch sang tiếng Việt
    return day_mapping.get(eng_day, "Không xác định")


import datetime


def get_remaining_days(input_date=None):
    """
    Trả về danh sách các ngày còn lại trong tuần (bao gồm ngày hiện tại), với mỗi ngày đại diện bằng số (2 = Thứ 2, ..., 8 = CN).
    :param input_date: Ngày (kiểu datetime.date). Mặc định là ngày hôm nay.
    :return: Danh sách các ngày còn lại trong tuần (dạng mảng số).
    """
    # Lấy ngày hiện tại nếu không truyền tham số
    if input_date is None:
        input_date = datetime.date.today()

    # Lấy thứ của ngày hiện tại (0 = Thứ Hai, ..., 6 = Chủ Nhật)
    current_day_index = input_date.weekday()

    # Chuyển current_day_index về dạng số tương ứng (2 = Thứ 2, ..., 8 = CN)
    # Kết quả sẽ là [2, 3, ..., 8] tương ứng với các ngày còn lại trong tuần
    remaining_days = [i + 2 for i in range(current_day_index, 7)]

    return remaining_days



def count_so_phan_tu(object):
    return object.query.count()

def count_user_theo_vaitro(vaitro):
    users = User.query.filter(User.vaitro == vaitro)
    return users.count()

def so_phan_tu(page, query=None):
    page_size = app.config['SO_PHAN_TU']
    start = (page - 1) * page_size  # Ví dụ lấy từ trang 1: (1-1)*8 = 0
    query = query.slice(start, start + page_size)  # Từ vị trí số 0 lấy thêm 8 phần tử
    return query

def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username),
                          User.password.__eq__(password))
    if role:
        u = u.filter(User.vaitro.__eq__(role))

    return u.first()


def get_user_by_id(user_id):
    return User.query.get(user_id)  # Truy vấn trong bảng dữ liệu để lấy user_id

def load_object(object):
    query = object.query.order_by("id")
    return query.all()

def load_bs(chuyennganh=None):
    query = User.query.filter(User.vaitro == UserRole.BACSI)

    if chuyennganh:
        query = db.session.query(User.id, User.ten, ChuyenNganh.ten).select_from(User).join(ChuyenNganh)
        query = query.filter(User.vaitro == UserRole.BACSI, ChuyenNganh.id == chuyennganh)

    return query.all()


def load_bstrucca(chuyennganh=None):
    """
    Lấy danh sách các bác sĩ trực ca dựa trên lịch khám (isTrong = True) và thông tin khung giờ.

    :param chuyennganh: (Optional) Lọc theo chuyên ngành bác sĩ.
    :return: Danh sách bác sĩ với thông tin lịch trực ca và khung giờ.
    """
    # Gọi hàm load_bs để lấy danh sách bác sĩ theo chuyên ngành (User.vaitro == UserRole.BACSI)
    bacsi_query = load_bs(chuyennganh)

    # Thực hiện truy vấn chính, kết hợp với các bảng liên quan như KhungGio
    query = db.session.query(
        User.ten.label("bacsi_ten"),
        ChuyenNganh.ten.label("chuyennganh_ten"),
        KhungGio.khoangthoigian.label("khunggio_ten"),
    ).join(LichKham, LichKham.user_id == User.id) \
        .join(KhungGio, LichKham.khunggio_id == KhungGio.id) \
        .join(ChuyenNganh, ChuyenNganh.id == User.chuyennganh_id) \
        .filter(User.id.in_([b.id for b in bacsi_query]), LichKham.isTrong == True)

    return query.all()



def load_hoadon(page = 1, date = datetime.date.today()):  # Load danh mục sản phẩm
    # query = db.session.query(HoaDon, PhieuKhamBenh, User).select_from(HoaDon).join(PhieuKhamBenh).join(User)
    # if date:
    #     query = query.filter(HoaDon. == cate_id)

    query = db.session.query(
        HoaDon.id.label('hoadon_id'),
        HoaDon.value.label('hoadon_value'),
        HoaDon.isThanhtoan.label('hoadon_isThanhtoan'),
        BenhNhan.ten.label('benhnhan_ten'),
        BenhNhan.sdt.label('benhnhan_sdt'),
        BenhNhan.gioitinh.label('benhnhan_gioitinh'),
        BenhNhan.ngaysinh.label('benhnhan_ngaysinh'),
        PhieuKhamBenh.ngaykham.label('phieukham_ngaykham')
    ).select_from(HoaDon) \
        .join(PhieuKhamBenh, HoaDon.phieukhambenh_id == PhieuKhamBenh.id) \
        .join(BenhNhan, PhieuKhamBenh.benhnhan_id == BenhNhan.id) \
        .join(User, HoaDon.user_id == User.id) \
        .order_by(HoaDon.id)

    query = so_phan_tu(page, query)

    result = [
        {
            "id": hoadon_id,
            "ten": benhnhan_ten,
            "sdt": benhnhan_sdt,
            "gioitinh": benhnhan_gioitinh,
            "value": hoadon_value,
            "isThanhtoan": hoadon_isThanhtoan,
            "ngaysinh": benhnhan_ngaysinh,
            "ngaykham": phieukham_ngaykham
        }
        for
        hoadon_id, hoadon_value, hoadon_isThanhtoan, benhnhan_ten, benhnhan_sdt, benhnhan_gioitinh, benhnhan_ngaysinh, phieukham_ngaykham
        in query.all()
    ]

    return result

def tim_hoadon(hoadonid):
    query = HoaDon.query.filter(HoaDon.id == hoadonid)
    return query.first()

def load_phieukhambenh():
    query = db.session.query(PhieuKhamBenh, BenhNhan, User).select_from(PhieuKhamBenh).join(BenhNhan).join(User)
    return query.all()

def load_sobntoida():
    sobntoida = app.config['SO_BENH_NHAN_TRONG_NGAY']
    return sobntoida

def dang_ky_kham(tenbn, sdtbn, emailbn, sinhbn, gioibn, trieuchungbn, lichkhambn):
    u = User(ten=tenbn, sdt=sdtbn, ngaysinh=sinhbn, gioitinh=gioibn)

def check_benhnhan(sdt):
    """
    Kiểm tra xem số điện thoại có tồn tại trong bảng BenhNhan.
    Trả về (True, thông tin_bệnh_nhân) nếu tồn tại, ngược lại trả về (False, None).
    """
    benhnhan = BenhNhan.query.filter(BenhNhan.sdt == sdt).first()  # Tìm bệnh nhân theo số điện thoại
    if benhnhan:
        patient_info = {
            "ten": benhnhan.ten,
            "ngaysinh": benhnhan.ngaysinh,
            "gioitinh": benhnhan.gioitinh,
            "sdt": benhnhan.sdt,
            "email": benhnhan.email
        }
        return True, patient_info
    return False, None

def medicine_rates_month_stats(month):
    return db.session.query(Thuoc.ten,
                            DonViThuoc.donvi,
                            func.sum(ChiTietPhieuKham.soluongthuoc),
                            func.count(ChiTietPhieuKham.thuoc_id)) \
        .join(ChiTietPhieuKham, ChiTietPhieuKham.thuoc_id.__eq__(Thuoc.id)) \
        .join(DonViThuoc).join(PhieuKhamBenh) \
        .filter(extract('month', PhieuKhamBenh.ngaykham).__eq__(month)) \
        .group_by(Thuoc.id).all()

def tansuatkham(month):
    return (db.session.query(extract('day', PhieuKhamBenh.ngaykham ),
                            func.count(PhieuKhamBenh.id))) \
            .filter(extract('month', PhieuKhamBenh.ngaykham).__eq__(month)) \
            .group_by (extract('day', PhieuKhamBenh.ngaykham)) \
            .order_by(extract('day', PhieuKhamBenh.ngaykham)).all()

if __name__ == '__main__':  # Tự phát hiện cái bảng này chưa có và nó tạo ra
    with app.app_context():
        print(check_benhnhan('0123456781'))

