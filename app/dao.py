import datetime

from app.models import User, HoaDon, PhieuKhamBenh, BenhNhan  # Dùng DL trong bảng dữ liệu
from app import app, db  # Import để lấy các thông số cấu hình, db để thêm vào CSDL
import hashlib

def count_so_phan_tu(object):
    return object.query.count()

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


def load_hoadon(page = 1, date = datetime.date.today()):  # Load danh mục sản phẩm
    # query = db.session.query(HoaDon, PhieuKhamBenh, User).select_from(HoaDon).join(PhieuKhamBenh).join(User)
    # if date:
        # query = query.filter(HoaDon. == cate_id)

    query = db.session.query(
        HoaDon, PhieuKhamBenh, BenhNhan, User
    ).select_from(HoaDon) \
        .join(PhieuKhamBenh, HoaDon.phieukhambenh_id == PhieuKhamBenh.id) \
        .join(BenhNhan, PhieuKhamBenh.benhnhan_id == BenhNhan.id) \
        .join(User, HoaDon.user_id == User.id) \
        .order_by(HoaDon.id)




    query = so_phan_tu(page, query)

    return query.all()

def load_phieukhambenh():
    query = db.session.query(PhieuKhamBenh, BenhNhan, User).select_from(PhieuKhamBenh).join(BenhNhan).join(User)
    return query.all()
