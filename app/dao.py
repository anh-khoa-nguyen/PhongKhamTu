import datetime
from datetime import date

from app.models import User, HoaDon, PhieuKhamBenh, BenhNhan, ChuyenNganh, UserRole, LichKham, KhungGio, PhieuDatLich, \
    DanhSachKham, PhieuKhamBenh, ChiTietPhieuKham, Thuoc, DonViThuoc, BinhLuan, PKBCoBenh, \
    LoaiBenh  # Dùng DL trong bảng dữ liệu

from app import app, db  # Import để lấy các thông số cấu hình, db để thêm vào CSDL
import hashlib
from sqlalchemy import extract, func
import cloudinary.uploader

from config import *
from twilio.rest import Client

def count_so_phan_tu(object):
    return object.query.count()

def load_object(object):
    query = object.query.order_by("id")
    return query.all()

def load_chuyennganh():
    query = ChuyenNganh.query.filter_by(isKham=1).order_by("id")
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

    guiTn(
        sdt=sdtbn,
        context="dang_ky_kham",
        ngay=ngaykhambn,
        user_id=bacsikhambn
    )

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

from sqlalchemy import func


# def load_hoadon(page=1, date=datetime.date.today(), danhsach_hoadon=None):
#     """
#     Hàm lấy danh sách hóa đơn, cho phép lọc kết quả dựa trên danh sách hóa đơn cụ thể (nếu được cung cấp).
#
#     :param page: Số trang (mặc định: 1)
#     :param date: Ngày cần lọc hóa đơn (mặc định: hôm nay)
#     :param danhsach_hoadon: Danh sách các hóa đơn để lọc (mặc định: None).
#     :return: Danh sách hóa đơn đã được xử lý.
#     """
#     query = db.session.query(
#         HoaDon.id.label('hoadon_id'),
#         HoaDon.isThanhtoan.label('hoadon_isThanhtoan'),
#         HoaDon.gia_kham.label('gia_kham'),
#         BenhNhan.ten.label('benhnhan_ten'),
#         BenhNhan.sdt.label('benhnhan_sdt'),
#         BenhNhan.gioitinh.label('benhnhan_gioitinh'),
#         BenhNhan.ngaysinh.label('benhnhan_ngaysinh'),
#         PhieuKhamBenh.ngaykham.label('phieukham_ngaykham'),
#         func.sum(Thuoc.gia * ChiTietPhieuKham.soluongthuoc).label("tong_tien_thuoc")
#     ).select_from(HoaDon) \
#         .join(PhieuKhamBenh, HoaDon.phieukhambenh_id == PhieuKhamBenh.id) \
#         .join(BenhNhan, PhieuKhamBenh.benhnhan_id == BenhNhan.id) \
#         .join(User, HoaDon.user_id == User.id) \
#         .join(ChiTietPhieuKham, ChiTietPhieuKham.phieukhambenh_id == PhieuKhamBenh.id) \
#         .join(Thuoc, ChiTietPhieuKham.thuoc_id == Thuoc.id) \
#         .group_by(HoaDon.id, BenhNhan.ten, BenhNhan.sdt, BenhNhan.gioitinh, BenhNhan.ngaysinh, PhieuKhamBenh.ngaykham)
#
#     # Nếu `danhsach_hoadon` được cung cấp, lọc theo danh sách này
#     if danhsach_hoadon:
#         # Trích xuất danh sách `id` từ các đối tượng `HoaDon`
#         hoadon_ids = [hd.id for hd in danhsach_hoadon]
#         query = query.filter(HoaDon.id.in_(hoadon_ids))
#
#     # Áp dụng phân trang
#     query = so_phan_tu(page, query)
#
#     result = [
#         {
#             "id": hoadon_id,
#             "ten": benhnhan_ten,
#             "sdt": benhnhan_sdt,
#             "gioitinh": benhnhan_gioitinh,
#             "isThanhtoan": hoadon_isThanhtoan,
#             "gia_kham": gia_kham,
#             "value": tong_tien_thuoc,  # Tổng số tiền thuốc (định dạng số)
#             "ngaysinh": benhnhan_ngaysinh,
#             "ngaykham": phieukham_ngaykham
#         }
#         for
#         hoadon_id, hoadon_isThanhtoan, gia_kham, benhnhan_ten, benhnhan_sdt, benhnhan_gioitinh, benhnhan_ngaysinh, phieukham_ngaykham, tong_tien_thuoc
#         in query.all()
#     ]
#
#     return result
def load_hoadon(page=1, date=datetime.date.today(), danhsach_hoadon=None, chitiet=False):
    """
    Hàm lấy danh sách hóa đơn, cho phép lọc kết quả dựa trên danh sách hóa đơn cụ thể (nếu được cung cấp).
    Khi chitiet=True, lấy thêm thông tin chi tiết phiếu khám và toa thuốc.

    :param page: Số trang (mặc định: 1)
    :param date: Ngày cần lọc hóa đơn (mặc định: hôm nay)
    :param danhsach_hoadon: Danh sách các hóa đơn để lọc (mặc định: None).
    :param chitiet: Nếu True, lấy thêm thông tin chi tiết phiếu khám và toa thuốc.
    :return: Danh sách hóa đơn đã được xử lý.
    """
    if danhsach_hoadon is not None and len(danhsach_hoadon) == 0:
        return []

    query = db.session.query(
        HoaDon.id.label('hoadon_id'),
        HoaDon.isThanhtoan.label('hoadon_isThanhtoan'),
        HoaDon.ngaytao.label('ngay_tao'),
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
        .group_by(HoaDon.id, BenhNhan.ten, BenhNhan.sdt, BenhNhan.gioitinh, BenhNhan.ngaysinh, PhieuKhamBenh.ngaykham)\
        .order_by(HoaDon.id)
    # Nếu `danhsach_hoadon` được cung cấp, lọc theo danh sách này
    if danhsach_hoadon:
        # Trích xuất danh sách `id` từ các đối tượng `HoaDon`
        hoadon_ids = [hd.id for hd in danhsach_hoadon]
        query = query.filter(HoaDon.id.in_(hoadon_ids))

    # Áp dụng phân trang
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
            "ngaykham": phieukham_ngaykham,
            "ngaytao": ngay_tao
        }
        for
        hoadon_id, hoadon_isThanhtoan, ngay_tao, gia_kham, benhnhan_ten, benhnhan_sdt, benhnhan_gioitinh, benhnhan_ngaysinh, phieukham_ngaykham, tong_tien_thuoc
        in query.all()
    ]

    # Nếu `chitiet=True`, lấy thêm chi tiết hóa đơn
    if chitiet:
        for hoadon in result:
            chi_tiet_query = db.session.query(
                ChiTietPhieuKham.soluongthuoc,  # Số lượng thuốc
                Thuoc.ten.label("tenthuoc"),  # Tên thuốc
                Thuoc.gia.label("dongia"),  # Đơn giá
            ).select_from(ChiTietPhieuKham) \
                .join(Thuoc, ChiTietPhieuKham.thuoc_id == Thuoc.id) \
                .filter(ChiTietPhieuKham.phieukhambenh_id == PhieuKhamBenh.id) \
                .filter(PhieuKhamBenh.id == HoaDon.query.get(hoadon["id"]).phieukhambenh_id)

            hoadon["chitiet"] = [
                {
                    "tenthuoc": row.tenthuoc,
                    "soluongthuoc": row.soluongthuoc,
                    "gia": row.dongia,
                }
                for row in chi_tiet_query.all()
            ]

    return result


def tim_hoadon(hoadonid):
    return HoaDon.query.filter(HoaDon.id == hoadonid).all()


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
                patient_sdt = pdl.benhnhan.sdt
                guiTn(
                    sdt=patient_sdt,
                    context="create_danhsachkham",
                    ngay=ngay,
                    user_id=pdl.user_id
                )

            # Kiểm tra số lượng bệnh nhân
            total_benh_nhan = len(phieu_dat_lichs)
            if total_benh_nhan > sobnmax:
                raise ValueError(f"Số bệnh nhân trong ngày {ngay} vượt quá giới hạn ({sobnmax}).")

            db.session.commit()
            return f"Đã tạo mới danh sách khám {ds_kham.id} với {total_benh_nhan} phiếu đặt lịch."

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Lỗi khi xử lý danh sách khám: {str(e)}")

# Trang
def check_danhsachhd(ngay):
    """
    Lọc ra danh sách các hóa đơn theo ngày khám.
    :param ngay: Ngày cần lọc (string, định dạng 'YYYY-MM-DD')
    :return: Danh sách các hóa đơn theo ngày khám
    """
    # Chuyển ngày từ chuỗi sang kiểu datetime
    ngay_datetime = datetime.datetime.strptime(ngay, '%Y-%m-%d').date()

    # Truy vấn các hóa đơn theo ngày khám, join với bảng PhieuKhamBenh
    query = HoaDon.query.join(PhieuKhamBenh, HoaDon.phieukhambenh_id == PhieuKhamBenh.id).filter(
        extract('year', PhieuKhamBenh.ngaykham) == ngay_datetime.year,
        extract('month', PhieuKhamBenh.ngaykham) == ngay_datetime.month,
        extract('day', PhieuKhamBenh.ngaykham) == ngay_datetime.day
    )

    return query.all()


def update_hoadon(hoadon_id):
    """
    Cập nhật trạng thái isThanhtoan thành True cho một hóa đơn.
    :param hoadon_id: ID của hóa đơn cần cập nhật
    """
    try:
        hoadon = HoaDon.query.get(hoadon_id)
        if not hoadon:
            raise Exception("Không tìm thấy hóa đơn với ID được cung cấp.")

        hoadon.isThanhtoan = True
        db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu
    except Exception as e:
        db.session.rollback()  # Hoàn tác nếu có lỗi
        raise Exception(f"Lỗi khi cập nhật hóa đơn: {str(e)}")

#Lập phiếu khám
def save_chitiet_phieukham(phieu_kham_id, drug_id, quantity):
    from app.models import ChiTietPhieuKham  # Import model của chi tiết phiếu khám
    from app import db  # SQLAlchemy database session

    try:
        # Tạo một bản ghi mới trong bảng ChiTietPhieuKham
        chitiet_phieukham = ChiTietPhieuKham(
            phieukhambenh_id=phieu_kham_id,
            thuoc_id=drug_id,
            soluongthuoc=quantity
        )

        db.session.add(chitiet_phieukham)  # Lưu dữ liệu vào session
        update_tonkho(drug_id, quantity)
        db.session.commit()  # Commit thay đổi vào database

    except Exception as e:
        # Nếu có lỗi xảy ra, rollback để không phá vỡ dữ liệu
        db.session.rollback()
        raise Exception(f"Lỗi khi lưu chi tiết phiếu khám: {str(e)}")

def update_tonkho(thuoc_id, used_quantity):
    """
    Hàm cập nhật tồn kho của thuốc
    :param thuoc_id: ID của thuốc cần cập nhật
    :param used_quantity: Số lượng thuốc cần giảm
    :raises Exception: Nếu tồn kho không đủ hoặc không tìm thấy thuốc
    """
    try:
        # Lấy thuốc từ cơ sở dữ liệu
        thuoc = Thuoc.query.get(thuoc_id)

        # Nếu không tìm thấy thuốc
        if not thuoc:
            raise Exception(f"Không tìm thấy thuốc với ID: {thuoc_id}")

        # Kiểm tra tồn kho hiện tại
        if thuoc.tonkho < used_quantity:
            raise Exception(
                f"Không đủ tồn kho cho thuốc {thuoc.ten}. Hiện tại còn: {thuoc.tonkho}, cần: {used_quantity}")

        # Tiến hành cập nhật tồn kho
        thuoc.tonkho -= used_quantity

        # Commit thay đổi vào database
        db.session.commit()

    except Exception as e:
        # Rollback nếu có lỗi
        db.session.rollback()
        raise Exception(f"Lỗi khi cập nhật tồn kho thuốc: {str(e)}")


def save_phieu_kham_va_cobenh(patient_id, ngay_kham, user_id, loaibenh_id):
    """
    Lưu phiếu khám bệnh (PhieuKhamBenh) và liên kết loại bệnh vào pkb-cobenh.

    Args:
        patient_id (int): ID bệnh nhân.
        ngay_kham (datetime): Ngày khám.
        user_id (int): ID người dùng (bác sĩ).
        loaibenh_id (int): ID của loại bệnh.

    Returns:
        int: ID của phiếu khám bệnh mới được tạo.
    """
    from app.models import PhieuKhamBenh, PKBCoBenh  # Import các model cần thiết
    from app import db  # SQLAlchemy session management

    try:
        # 1. Tạo phiếu khám bệnh
        phieu_kham = PhieuKhamBenh(
            benhnhan_id=patient_id,
            ngaykham=ngay_kham,
            user_id=user_id
        )
        db.session.add(phieu_kham)
        db.session.flush()  # Đẩy dữ liệu xuống DB để lấy pkb_id

        # 2. Lấy ID phiếu khám vừa tạo
        pkb_id = phieu_kham.id

        # 3. Tạo mối quan hệ với Loại Bệnh trong bảng PKBCoBenh
        pkb_cobenh = PKBCoBenh(
            phieukhambenh_id=pkb_id,
            loaibenh_id=loaibenh_id
        )
        db.session.add(pkb_cobenh)

        # 4. Commit dữ liệu vào database
        # db.session.commit()
        # for drug in drugs:
        #     drug_id = drug.get('drugName')
        #     quantity = drug.get('quantity')
        #
        #     if drug_id and quantity:
        #         chitietPK = ChiTietPhieuKham(
        #             phieukhambenh_id=phieu_kham.id,
        #             thuoc_id=drug_id,
        #             soluong=quantity
        #         )
        #         db.session.add(chitietPK)

        # 3. Commit tất cả thay đổi
        db.session.commit()

        # 5. Trả về ID của phiếu khám bệnh vừa tạo
        return pkb_id

    except Exception as e:
        # Nếu gặp lỗi, rollback toàn bộ giao dịch
        db.session.rollback()
        raise Exception(f"Lỗi khi lưu phiếu khám bệnh và pkb-cobenh: {str(e)}")

def get_all_drugs():
    # Truy vấn toàn bộ thuốc từ cơ sở dữ liệu
    drugs = db.session.query(
        Thuoc.id,
        Thuoc.ten,
        Thuoc.gia,
        DonViThuoc.donvi,
        Thuoc.tonkho
    ).join(DonViThuoc, Thuoc.donvithuoc_id == DonViThuoc.id).all()

    # Định dạng dữ liệu trả về
    drug_list = [
        {
            "id": drug.id,
            "ten": drug.ten,
            "gia": drug.gia,
            "donvi": drug.donvi,
            "tonkho": drug.tonkho
        }
        for drug in drugs
    ]

    return drug_list

def load_paitients(id):
    benhnhan = BenhNhan.query.filter(BenhNhan.id == id).first()  # Tìm bệnh nhân theo ID
    if benhnhan:
        patient_info = {
            "ten": benhnhan.ten,
            "ngaysinh": format_date(benhnhan.ngaysinh),  # Định dạng lại ngày sinh
            "sdt": benhnhan.sdt,
        }
        return True, patient_info
    return False, None

def format_date(date_obj):
    try:
        if isinstance(date_obj, datetime):  # Kiểm tra xem có phải kiểu datetime
            return date_obj.strftime("%d/%m/%Y")  # Định dạng thành dd/mm/yyyy
        return date_obj  # Nếu không phải datetime, trả về gốc
    except Exception as e:
        print(f"Error formatting date: {e}")
        return date_obj

def get_thuoc_id_by_name(thuoc_ten):
    """
       Truy vấn ID của thuốc dựa vào tên thuốc.
       :param thuoc_ten: Tên thuốc (string).
       :return: ID của thuốc (int) hoặc None nếu không tìm thấy.
       """
    from app.models import Thuoc
    thuoc = Thuoc.query.filter(Thuoc.ten == thuoc_ten).first()
    return thuoc.id

def get_chitietphieukham_by_benhnhan_id(benhnhan_id):
    # Truy vấn danh sách phiếu khám theo bệnh nhân ID
    chitietphieus = db.session.query(ChiTietPhieuKham, Thuoc) \
        .join(Thuoc, ChiTietPhieuKham.thuoc_id == Thuoc.id) \
        .filter(ChiTietPhieuKham.phieukhambenh_id == PhieuKhamBenh.id) \
        .filter(PhieuKhamBenh.benhnhan_id == benhnhan_id).all()

    result = []
    for ct, thuoc in chitietphieus:
        result.append({
            "tenthuoc": thuoc.ten,
            "donvitinh": thuoc.donvithuoc.donvi,
            "soluong": ct.soluongthuoc,
            "trongkho": thuoc.tonkho,
            "gia": thuoc.gia,
            "tongcong": ct.soluongthuoc * thuoc.gia
        })
    return result

def load_loaibenh():
    try:
        # Truy vấn danh sách các loại bệnh
        loaibenhs = db.session.query(LoaiBenh).all()

        # Chuyển đổi dữ liệu thành danh sách các dict
        loaibenh_list = [
            {"id": loaibenh.id, "ten": loaibenh.ten}
            for loaibenh in loaibenhs
        ]

        return loaibenh_list
    except Exception as e:
        print(f"Lỗi khi truy vấn loại bệnh: {e}")
        return []

def get_lichsu_khambenh_by_benhnhan_id(benhnhan_id):
    # Truy vấn thông tin lịch sử khám bệnh
    lichsu = db.session.query(
        PhieuKhamBenh.id.label('phieukhambenh_id'),
        PhieuKhamBenh.ngaykham,
        BenhNhan.ten.label('tenbenhnhan'),
        BenhNhan.ngaysinh.label('ngaysinhbenhnhan'),
        db.func.group_concat(LoaiBenh.ten).label('chuandoan')  # Ghép tên các loại bệnh liên quan
    ).join(BenhNhan, PhieuKhamBenh.benhnhan_id == BenhNhan.id) \
        .join(PKBCoBenh, PhieuKhamBenh.id == PKBCoBenh.phieukhambenh_id) \
        .join(LoaiBenh, PKBCoBenh.loaibenh_id == LoaiBenh.id) \
        .filter(BenhNhan.id == benhnhan_id) \
        .group_by(PhieuKhamBenh.id, BenhNhan.ten, BenhNhan.ngaysinh) \
        .order_by(PhieuKhamBenh.ngaykham.desc()) \
        .all()

    result = []
    for item in lichsu:
        result.append({
            'phieukhambenh_id': item.phieukhambenh_id,
            'ngaykham': item.ngaykham.strftime('%Y-%m-%d %H:%M:%S'),
            'chuandoan': item.chuandoan.replace(",", ", "),  # Format lại hiển thị danh sách loại bệnh
            'tenbenhnhan': item.tenbenhnhan,
            'ngaysinhbenhnhan': item.ngaysinhbenhnhan.strftime('%Y-%m-%d')
        })
    return result

def get_chitiet_donthuoc_by_phieukhambenh_id(phieukhambenh_id):
    """
    Lấy chi tiết đơn thuốc kèm theo tổng số tiền cần thanh toán
    """
    # Truy vấn chi tiết đơn thuốc từ database
    chitiet = db.session.query(ChiTietPhieuKham, Thuoc) \
        .join(Thuoc, ChiTietPhieuKham.thuoc_id == Thuoc.id) \
        .filter(ChiTietPhieuKham.phieukhambenh_id == phieukhambenh_id).all()

    result = []
    tong_tien = 0  # Biến để lưu tổng tiền

    for ct, thuoc in chitiet:
        # Tính tổng cộng từng loại thuốc
        tong_cong = ct.soluongthuoc * thuoc.gia
        tong_tien += tong_cong  # Cộng dồn vào tổng tiền

        # Thêm thông tin vào danh sách kết quả
        result.append({
            'tenthuoc': thuoc.ten,
            'donvitinh': thuoc.donvithuoc.donvi,
            'soluong': ct.soluongthuoc,
            'trongkho': thuoc.tonkho,
            'gia': thuoc.gia,
            'tongcong': tong_cong
        })

    return {'chitiet': result, 'tong_tien': tong_tien}


def tra_bacsi_va_khunggio(user_id, ngay):
    """
    Trả về khung giờ và tên bác sĩ dựa trên user_id và chuỗi ngày 'ngay'.

    :param user_id: ID của bác sĩ.
    :param ngay: Chuỗi ngày (định dạng "YYYY-MM-DD").
    :return: Tuple (khung_gio, bac_si_name).
    """
    try:
        # Chuyển chuỗi ngày sang đối tượng datetime.date
        ngay_date = datetime.datetime.strptime(ngay, '%Y-%m-%d').date()
    except ValueError:
        # Trường hợp chuỗi ngày không hợp lệ
        return "Ngày không hợp lệ", "Không rõ bác sĩ"

    # Truy vấn lịch khám dựa trên ngay_date
    lich_kham = LichKham.query.filter_by(user_id=user_id, ngay=ngay_date).first()
    khung_gio = lich_kham.khunggio.khoangthoigian if lich_kham else "Không rõ"

    # Truy vấn thông tin bác sĩ
    bac_si = User.query.filter_by(id=user_id, vaitro=UserRole.BACSI).first()
    bac_si_name = bac_si.ten if bac_si else "Không rõ bác sĩ"

    return khung_gio, bac_si_name


def guiTn(sdt, ngay=None, user_id=None, context="dang_ky_kham", **kwargs):
    """
    Gửi tin nhắn với nội dung tùy chỉnh dựa trên context.

    :param sdt: Số điện thoại.
    :param ngay: Ngày đăng ký khám.
    :param user_id: ID của bác sĩ (user_id liên quan).
    :param context: Ngữ cảnh gọi hàm.
    :param kwargs: Các tham số bổ sung như bệnh nhân, dịch vụ, v.v...
    """
    # Chuẩn hóa định dạng số điện thoại
    if sdt.startswith("0"):
        sdt = "+84" + sdt[1:]
    elif not sdt.startswith("+84"):
        sdt = "+84" + sdt

    # Dynamic Retrieval of khung_gio and bac_si
    khung_gio, bac_si_name = tra_bacsi_va_khunggio(user_id, ngay)

    # Generate message based on context
    if context == "dang_ky_kham":
        message_body = (
            f"Đăng ký lịch khám thành công! Vui lòng đến vào ngày {ngay} "
            f"trong khung giờ {khung_gio} để được khám bởi bác sĩ {bac_si_name}."
        )
    elif context == "create_danhsachkham":
        message_body = (
            f"Danh sách khám ngày {ngay} đã sẵn sàng! Khung giờ: {khung_gio} - "
            f"Bác sĩ điều trị: {bac_si_name}"
        )
    else:
        message_body = "Thông báo quan trọng từ phòng khám!"

    # Sending SMS (Example using Twilio)
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message_body,
        from_=twilio_phone,
        to=sdt
    )

    # Log message ID for confirmation
    print(message.sid)
    print("Tin nhắn đã được gửi thành công!")




if __name__ == '__main__':
    with app.app_context():
        print(tra_bacsi_va_khunggio(5, ngay = '2024-12-27'))

