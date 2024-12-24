from app import app, db
from models import HoaDon  # Đảm bảo đúng đường dẫn đến model HoaDon

# Đặt giá khám mặc định trên tất cả các bản ghi HoaDon cũ
with app.app_context():
    for hoadon in HoaDon.query.all():
        if hoadon.gia_kham is None:  # Trong trường hợp bạn chưa có giá khám cũ
            hoadon.gia_kham = app.config['SO_TIEN_KHAM']  # Lấy giá khám mặc định hiện tại
    db.session.commit()

print("Cập nhật giá khám thành công cho các hóa đơn cũ.")