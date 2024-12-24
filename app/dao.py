import datetime
from datetime import date

from app.models import User, HoaDon, PhieuKhamBenh, BenhNhan, ChuyenNganh, UserRole, LichKham, KhungGio, PhieuDatLich, \
    DanhSachKham, PhieuKhamBenh, ChiTietPhieuKham, Thuoc, DonViThuoc, BinhLuan  # Dùng DL trong bảng dữ liệu

from app import app, db  # Import để lấy các thông số cấu hình, db để thêm vào CSDL
import hashlib
from sqlalchemy import extract, func
import cloudinary.uploader

def count_so_phan_tu(object):
    return object.query.count()

def load_object(object):
    query = object.query.order_by("id")
    return query.all()

# Trang đặt lịch khám
def count_so_bn_kham_theo_ngay(ngay):
    # Truy vấn chỉ lọc theo phần "ngày" của cột ngaydatlich
    query = PhieuDatLich.query.filter(
        func.date(PhieuDatLich.ngaydatlich) == ngay
    )
    return query.count()

def so_phan_tu(page, query=None):
    page_size = app.config['SO_PHAN_TU']
    start = (page - 1) * page_size  # Ví dụ lấy từ trang 1: (1-1)*8 = 0
    query = query.slice(start, start + page_size)  # Từ vị trí số 0 lấy thêm 8 phần tử
    return query

def get_remaining_days(input_date=None):
    """
    Trả về danh sách các ngày còn lại trong tuần (bao gồm ngày hiện tại),
    với mỗi ngày là tuple gồm (thứ, ngày cụ thể).

    :param input_date: Ngày (kiểu datetime.date). Mặc định là ngày hôm nay.
    :return: Mảng tuple (thứ, ngày cụ thể).
    """
    # Lấy ngày hiện tại nếu không truyền tham số
    if input_date is None:
        input_date = datetime.date.today()

    # Lấy thứ của ngày hiện tại (0 = Thứ Hai, ..., 6 = Chủ Nhật)
    current_day_index = input_date.weekday()

    # Tạo danh sách các ngày còn lại trong tuần
    remaining_days = []

    sobnmax = load_sobntoida()  # Giới hạn khám mỗi ngày

    for i in range(current_day_index, 7):
        # Tính ngày cụ thể
        day_date = input_date + datetime.timedelta(days=(i - current_day_index))
        # Tính thứ (2 = Thứ 2, ..., 8 = CN)
        day_number = i + 2
        # Lấy ngày dạng chuỗi
        ngay_str = day_date.strftime('%Y-%m-%d')
        # Đếm số bệnh nhân đã khám trong ngày đó
        so_bn = count_so_bn_kham_theo_ngay(ngay_str)
        # Kiểm tra tình trạng (True nếu còn chỗ, False nếu đã đủ)
        tinh_trang = so_bn < sobnmax
        # Thêm vào danh sách kết quả, bao gồm (thứ, ngày, tình trạng)
        remaining_days.append((day_number, ngay_str, tinh_trang))
    return remaining_days

def load_bs(chuyennganh=None, tenbs = None):
    query = User.query.filter(User.vaitro == UserRole.BACSI)

    if chuyennganh:
        query = db.session.query(User.id, User.ten, ChuyenNganh.ten).select_from(User).join(ChuyenNganh)
        query = query.filter(User.vaitro == UserRole.BACSI, ChuyenNganh.id == chuyennganh)

    if tenbs:
        query = query.filter(User.vaitro == UserRole.BACSI, User.ten == tenbs)

    return query.all()

def load_bstrucca(chuyennganh=None, ngay=datetime.date.today()):
    """
    Lấy danh sách các bác sĩ trực ca dựa trên lịch khám (isTrong = True) và thông tin khung giờ.

    :param chuyennganh: (Optional) Lọc theo chuyên ngành bác sĩ.
    :return: Danh sách bác sĩ với thông tin lịch trực ca và khung giờ.
    """
    # Gọi hàm load_bs để lấy danh sách bác sĩ theo chuyên ngành (User.vaitro == UserRole.BACSI)
    bacsi_query = load_bs(chuyennganh)

    # Truy vấn lịch trực ca của bác sĩ theo ngày và chuyên ngành
    query = db.session.query(
        User.ten.label("bacsi_ten"),
        ChuyenNganh.ten.label("chuyennganh_ten"),
        KhungGio.khoangthoigian.label("khunggio_ten"),
        KhungGio.id.label("khunggio_id")
    ).join(LichKham, LichKham.user_id == User.id) \
        .join(KhungGio, LichKham.khunggio_id == KhungGio.id) \
        .join(ChuyenNganh, ChuyenNganh.id == User.chuyennganh_id) \
        .filter(User.id.in_([b.id for b in bacsi_query])) \
        .filter(LichKham.isTrong == True, LichKham.ngay == ngay)  # Lọc theo ngày và lịch còn trống

    return query.all()

def check_benhnhan(sdt):
    """
    Kiểm tra xem số điện thoại có tồn tại trong bảng BenhNhan.
    Trả về (True, thông tin_bệnh_nhân) nếu tồn tại, ngược lại trả về (False, None).
    """
    benhnhan = BenhNhan.query.filter(BenhNhan.sdt == sdt).first()  # Tìm bệnh nhân theo số điện thoại
    if benhnhan:
        patient_info = {
            "id": benhnhan.id,
            "ten": benhnhan.ten,
            "ngaysinh": benhnhan.ngaysinh,
            "gioitinh": benhnhan.gioitinh,
            "sdt": benhnhan.sdt,
            "email": benhnhan.email
        }
        return True, patient_info
    return False, None

def dang_ky_kham(tenbn, sdtbn, emailbn, sinhbn, gioibn, trieuchungbn, bacsikhambn, ngaykhambn, giokhambn):
    # Kiểm tra số bệnh nhân trong ngày
    if count_so_bn_kham_theo_ngay(ngaykhambn) >= load_sobntoida():
        # Nếu vượt giới hạn, trả thông báo lỗi (kết thúc sớm hàm)
        raise ValueError(f"Lịch khám ngày {ngaykhambn} đã đầy, vui lòng chọn ngày khác.")

    # Kiểm tra xem bệnh nhân đã tồn tại dựa trên số điện thoại
    is_exist, benhnhan_info = check_benhnhan(sdtbn)

    if is_exist:
        # Nếu bệnh nhân đã tồn tại, chỉ tạo phiếu đặt lịch mới
        phieudatlich = PhieuDatLich(
            benhnhan_id=benhnhan_info["id"],  # Lấy ID bệnh nhân từ thông tin đã có
            trieuchung=trieuchungbn,
            user_id=bacsikhambn,  # Bác sĩ phụ trách
            ngaydatlich=ngaykhambn
        )
        db.session.add(phieudatlich)
    else:
        # Nếu bệnh nhân chưa tồn tại, tạo mới bệnh nhân và phiếu đặt lịch
        benhnhan = BenhNhan(
            ten=tenbn,
            sdt=sdtbn,
            ngaysinh=sinhbn,
            gioitinh=gioibn,
            email=emailbn
        )
        db.session.add(benhnhan)  # Thêm bệnh nhân vào cơ sở dữ liệu

        # Tạo phiếu đặt lịch mới
        phieudatlich = PhieuDatLich(
            benhnhan=benhnhan,  # Sử dụng ID của bệnh nhân vừa tạo
            trieuchung=trieuchungbn,
            user_id=bacsikhambn,
            ngaydatlich=ngaykhambn
        )
        db.session.add(phieudatlich)

    # Tìm lịch khám phù hợp với ngày và giờ khám được chọn
    lich_kham = LichKham.query.filter(
        LichKham.ngay == ngaykhambn,
        LichKham.khunggio_id == giokhambn,
        LichKham.isTrong == True  # Chỉ lấy những lịch còn trống
    ).first()
    if lich_kham:
        # Nếu tìm thấy, cập nhật isTrong thành False (0)
        lich_kham.isTrong = False

    # Commit tất cả các thay đổi vào cơ sở dữ liệu
    db.session.commit()

# Đăng nhập
def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    u = User.query.filter(User.username.__eq__(username),
                          User.password.__eq__(password))
    if role:
        u = u.filter(User.vaitro.__eq__(role))

    return u.first()

def get_user_by_id(user_id):
    return User.query.get(user_id)  # Truy vấn trong bảng dữ liệu để lấy user_id

# Trang hóa đơn
# Trang hóa đơn
# def load_hoadon(page=1, date=datetime.date.today()):
#     query = db.session.query(
#         HoaDon.id.label('hoadon_id'),
#         HoaDon.isThanhtoan.label('hoadon_isThanhtoan'),
#         HoaDon.gia_kham.label('gia_kham'),
#         BenhNhan.ten.label('benhnhan_ten'),
#         BenhNhan.sdt.label('benhnhan_sdt'),
#         BenhNhan.gioitinh.label('benhnhan_gioitinh'),
#         BenhNhan.ngaysinh.label('benhnhan_ngaysinh'),
#         PhieuKhamBenh.ngaykham.label('phieukham_ngaykham')
#     ).select_from(HoaDon) \
#         .join(PhieuKhamBenh, HoaDon.phieukhambenh_id == PhieuKhamBenh.id) \
#         .join(BenhNhan, PhieuKhamBenh.benhnhan_id == BenhNhan.id) \
#         .join(User, HoaDon.user_id == User.id) \
#         .order_by(HoaDon.id)
#
#     query = so_phan_tu(page, query)
#
#     result = [
#         {
#             "id": hoadon_id,
#             "ten": benhnhan_ten,
#             "sdt": benhnhan_sdt,
#             "gioitinh": benhnhan_gioitinh,
#             "isThanhtoan": hoadon_isThanhtoan,
#             "gia_kham": gia_kham,  # Thêm giá khám vào kết quả trả về
#             "ngaysinh": benhnhan_ngaysinh,
#             "ngaykham": phieukham_ngaykham
#         }
#         for
#         hoadon_id, hoadon_isThanhtoan, gia_kham, benhnhan_ten, benhnhan_sdt, benhnhan_gioitinh, benhnhan_ngaysinh, phieukham_ngaykham
#         in query.all()
#     ]
#
#     return result

from sqlalchemy import func


def load_hoadon(page=1, date=datetime.date.today()):
    query = db.session.query(
        HoaDon.id.label('hoadon_id'),
        HoaDon.isThanhtoan.label('hoadon_isThanhtoan'),
        HoaDon.gia_kham.label('gia_kham'),
        BenhNhan.ten.label('benhnhan_ten'),
        BenhNhan.sdt.label('benhnhan_sdt'),
        BenhNhan.gioitinh.label('benhnhan_gioitinh'),
        BenhNhan.ngaysinh.label('benhnhan_ngaysinh'),
        PhieuKhamBenh.ngaykham.label('phieukham_ngaykham'),
        func.sum(Thuoc.gia * ChiTietPhieuKham.soluongthuoc).label("tong_tien_thuoc")
    ).select_from(HoaDon) \
        .join(PhieuKhamBenh, HoaDon.phieukhambenh_id == PhieuKhamBenh.id) \
        .join(BenhNhan, PhieuKhamBenh.benhnhan_id == BenhNhan.id) \
        .join(User, HoaDon.user_id == User.id) \
        .join(ChiTietPhieuKham, ChiTietPhieuKham.phieukhambenh_id == PhieuKhamBenh.id) \
        .join(Thuoc, ChiTietPhieuKham.thuoc_id == Thuoc.id) \
        .group_by(HoaDon.id, BenhNhan.ten, BenhNhan.sdt, BenhNhan.gioitinh, BenhNhan.ngaysinh, PhieuKhamBenh.ngaykham)

    query = so_phan_tu(page, query)

    result = [
        {
            "id": hoadon_id,
            "ten": benhnhan_ten,
            "sdt": benhnhan_sdt,
            "gioitinh": benhnhan_gioitinh,
            "isThanhtoan": hoadon_isThanhtoan,
            "gia_kham": gia_kham,
            "value": tong_tien_thuoc,  # Tổng số tiền thuốc (định dạng số)
            "ngaysinh": benhnhan_ngaysinh,
            "ngaykham": phieukham_ngaykham
        }
        for
        hoadon_id, hoadon_isThanhtoan, gia_kham, benhnhan_ten, benhnhan_sdt, benhnhan_gioitinh, benhnhan_ngaysinh, phieukham_ngaykham, tong_tien_thuoc
        in query.all()
    ]

    return result

def tim_hoadon(hoadonid):
    query = HoaDon.query.filter(HoaDon.id == hoadonid)
    return query.first()

def load_phieukhambenh():
    query = db.session.query(PhieuKhamBenh, BenhNhan, User).select_from(PhieuKhamBenh).join(BenhNhan).join(User)
    return query.all()

#Trang thay đổi quy định
def load_sobntoida():
    sobntoida = app.config['SO_BENH_NHAN_TRONG_NGAY']
    return sobntoida

def load_sotienkham():
    sotienkham = app.config['SO_TIEN_KHAM']
    return sotienkham

# Trang thống kê

def medicine_rates_month_stats(month, year):
    return db.session.query(Thuoc.ten,
                            DonViThuoc.donvi,
                            func.sum(ChiTietPhieuKham.soluongthuoc),
                            func.count(ChiTietPhieuKham.thuoc_id)) \
        .join(ChiTietPhieuKham, ChiTietPhieuKham.thuoc_id.__eq__(Thuoc.id)) \
        .join(DonViThuoc).join(PhieuKhamBenh) \
        .filter(extract('month', PhieuKhamBenh.ngaykham).__eq__(month)) \
        .filter(extract('year', PhieuKhamBenh.ngaykham).__eq__(year)) \
        .group_by(Thuoc.id).all()

def tansuatkham(month, year):
    return (db.session.query(extract('day', PhieuKhamBenh.ngaykham),
                             func.count(PhieuKhamBenh.id))) \
        .filter(extract('month', PhieuKhamBenh.ngaykham).__eq__(month)) \
        .filter(extract('year', PhieuKhamBenh.ngaykham).__eq__(year)) \
        .group_by(extract('day', PhieuKhamBenh.ngaykham)) \
        .order_by(extract('day', PhieuKhamBenh.ngaykham)).all()

def count_profit_month(month):
    count = db.session.query(func.count(HoaDon.id)).filter(
        extract('month', HoaDon.ngaytao) == month).first()
    return count[0]

def doanhthu(month, year):
    # sotienkham = load_sotienkham()
    current_count_month = count_profit_month(month)
    return db.session.query(extract('day', HoaDon.ngaytao),
                             func.count(HoaDon.id),
                            (func.sum(Thuoc.gia * ChiTietPhieuKham.soluongthuoc) + (func.sum(HoaDon.gia_kham))).label("Tổng doanh thu"), \
                            (func.count(HoaDon.id) / current_count_month * 100)) \
            .join(PhieuKhamBenh, HoaDon.phieukhambenh_id == PhieuKhamBenh.id) \
            .join(ChiTietPhieuKham,ChiTietPhieuKham.phieukhambenh_id == PhieuKhamBenh.id) \
            .join(Thuoc, ChiTietPhieuKham.thuoc_id == Thuoc.id) \
            .filter(HoaDon.isThanhtoan == True) \
            .filter(extract('year', HoaDon.ngaytao).__eq__(year)) \
            .filter(extract('month', HoaDon.ngaytao).__eq__(month)) \
            .group_by(extract("day", HoaDon.ngaytao)) \
            .order_by(extract("day", HoaDon.ngaytao)).all()

def load_comments():
    query = BinhLuan.query.order_by(-BinhLuan.id)
    return query.all()

def add_comment(ten, nghenghiep, binhluan,star_value, avatar= None):
    u = BinhLuan(ten=ten, nghenghiep = nghenghiep, binhluan = binhluan, star_value = star_value)
    if avatar:
        res = cloudinary.uploader.upload(avatar) #Nó trả về một cái API (dữ liệu JSON)
        u.avatar = res.get('secure_url') #Lấy thuộc tính url từ res
    db.session.add(u)
    db.session.commit()

def create_hoa_don(phieukhambenh_id, user_id):
    # Lấy giá khám hiện tại
    gia_kham_hientai = app.config['SO_TIEN_KHAM']

    # Tạo hóa đơn mới
    hoadon = HoaDon(
        phieukhambenh_id=phieukhambenh_id,
        user_id=user_id,
        gia_kham=gia_kham_hientai  # Lưu giá khám tại thời điểm này
    )

    # Thêm vào DB
    db.session.add(hoadon)
    db.session.commit()
    return hoadon

# Trang danh sách khám
def check_danhsachkham(ngay):
    """
    Lọc ra danh sách các phiếu đặt lịch có ngày đặt lịch trùng với ngày được chọn.
    :param ngay: Ngày được chọn (string, định dạng 'YYYY-MM-DD')
    :return: Danh sách các phiếu đặt lịch
    """
    # Chuyển ngày từ chuỗi sang kiểu datetime
    ngay_datetime = datetime.datetime.strptime(ngay, '%Y-%m-%d').date()

    # Truy vấn các phiếu đặt lịch theo ngày
    query = PhieuDatLich.query.filter(
        extract('year', PhieuDatLich.ngaydatlich) == ngay_datetime.year,
        extract('month', PhieuDatLich.ngaydatlich) == ngay_datetime.month,
        extract('day', PhieuDatLich.ngaydatlich) == ngay_datetime.day
    )

    return query.all()

def create_danhsachkham(user_id, ngay):
    try:
        # Kiểm tra số bệnh nhân tối đa trong ngày từ cấu hình
        sobnmax = load_sobntoida()

        # Tìm danh sách khám đã tồn tại trong ngày
        ds_kham = DanhSachKham.query.filter(
            db.func.date(DanhSachKham.ngaylap) == datetime.datetime.strptime(ngay, '%Y-%m-%d').date()
        ).first()

        if ds_kham:
            # Nếu đã có danh sách khám, chỉ thêm phiếu đặt lịch mới vào danh sách này
            phieu_dat_lichs = PhieuDatLich.query.filter(
                db.func.date(PhieuDatLich.ngaydatlich) == datetime.datetime.strptime(ngay, '%Y-%m-%d').date(),
                PhieuDatLich.danhsachkham_id.is_(None)  # Lấy các phiếu chưa được gán danh sách
            ).all()

            # Kiểm tra số lượng bệnh nhân trong danh sách khám hiện tại và sau khi thêm
            so_benh_nhan_hien_tai = len(ds_kham.phieudatlichs)
            so_benh_nhan_moi = len(phieu_dat_lichs)

            if so_benh_nhan_hien_tai + so_benh_nhan_moi > sobnmax:
                raise ValueError(f"Số bệnh nhân trong danh sách vượt quá giới hạn ({sobnmax}).")

            # Gắn các phiếu đặt lịch vào danh sách khám hiện tại
            for pdl in phieu_dat_lichs:
                pdl.danhsachkham_id = ds_kham.id

            db.session.commit()
            return f"Đã cập nhật danh sách khám {ds_kham.id} với {so_benh_nhan_moi} phiếu đặt lịch mới."
        else:
            # Nếu chưa có danh sách khám, tạo mới
            ds_kham = DanhSachKham(user_id=user_id, ngaylap=ngay)
            db.session.add(ds_kham)
            db.session.commit()

            # Gán phiếu đặt lịch vào danh sách khám mới tạo
            phieu_dat_lichs = PhieuDatLich.query.filter(
                db.func.date(PhieuDatLich.ngaydatlich) == datetime.datetime.strptime(ngay, '%Y-%m-%d').date()
            ).all()

            for pdl in phieu_dat_lichs:
                pdl.danhsachkham_id = ds_kham.id

            # Kiểm tra số lượng bệnh nhân
            total_benh_nhan = len(phieu_dat_lichs)
            if total_benh_nhan > sobnmax:
                raise ValueError(f"Số bệnh nhân trong ngày {ngay} vượt quá giới hạn ({sobnmax}).")

            db.session.commit()
            return f"Đã tạo mới danh sách khám {ds_kham.id} với {total_benh_nhan} phiếu đặt lịch."

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Lỗi khi xử lý danh sách khám: {str(e)}")

if __name__ == '__main__':
    with app.app_context():
        create_danhsachkham(ngay='2024-12-24', user_id=3)
