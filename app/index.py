import datetime

from flask import render_template, request, redirect, session, jsonify
from app import app, login

import dao, json
from flask_login import login_user, logout_user #Ghi nhận trạng thái login, logout của session (Một phiên)
from app.models import ChuyenNganh, User, BinhLuan


@app.route("/", methods=['GET','POST'])
def index():
    err_msg = None
    total_comments = 0
    if request.method.__eq__('POST'):
        ten = request.form.get('name')
        nghenghiep = request.form.get('nghenghiep')
        binhluan = request.form.get('binhluan')
        avatar = request.files.get('avatar')
        star_value = request.form.get('rating')


        dao.add_comment(avatar=avatar, ten=ten, nghenghiep=nghenghiep, binhluan=binhluan, star_value=star_value)

        if not ten or not nghenghiep or not binhluan:
            err_msg = 'Vui lòng nhập đầy đủ thông tin bắt buộc'
        else:
            err_msg = 'Những đánh giá của bạn là động lực cho chúng tôi'
    total_comments = dao.count_so_phan_tu(BinhLuan)
    return render_template('index.html', binhluan = dao.load_comments(), total_comments=total_comments)

@app.route("/examine", methods=['GET', 'POST'])
def examine():
    err_msg = None
    try:
        if request.method.__eq__('POST'):  # Kiểm tra nếu form gửi POST
            tenbn = request.form.get('bnname')  # Lấy họ tên
            sdtbn = str(request.form.get('bnphone'))  # Lấy số điện thoại
            emailbn = request.form.get('bnemail')  # Email (không bắt buộc)
            sinhbn = request.form.get('bnsinh')  # Ngày sinh
            gioibn = request.form.get('bngioi')  # Giới tính
            gioibn = gioibn == 'True'
            trieuchungbn = request.form.get('bntrieuchung')  # Triệu chứng
            ngaykhambn = request.form.get('bnngaykham')  # Lịch khám (chọn radio button)
            tenbs_giokhambn = request.form.get('bnbacsi_giokham')
            tenbs, giokhambn = tenbs_giokhambn.split('|')
            bacsikhambn = (dao.load_bs(tenbs=tenbs))[0].id

            # import pdb
            # pdb.set_trace()

            # Kiểm tra thông tin bắt buộc
            if not tenbn or not sdtbn or not sinhbn or not ngaykhambn or not bacsikhambn:
                err_msg = 'Vui lòng nhập đầy đủ thông tin bắt buộc'
            elif len(sdtbn) != 10 or not sdtbn.isdigit():  # Kiểm tra số điện thoại đủ 10 số và chỉ chứa số
                err_msg = 'Số điện thoại phải chứa đúng 10 chữ số'
            else:
                # Gọi hàm của DAO để xử lý logic đăng ký lịch khám
                dao.dang_ky_kham(
                    tenbn=tenbn,
                    sdtbn=sdtbn,
                    emailbn=emailbn,
                    sinhbn=sinhbn,
                    gioibn=gioibn,
                    trieuchungbn=trieuchungbn,
                    bacsikhambn=bacsikhambn,
                    giokhambn=giokhambn,
                    ngaykhambn=ngaykhambn
                )
                err_msg = 'Đăng ký lịch khám thành công'

    except Exception as e:
        err_msg = f'Có lỗi xảy ra: {str(e)}'

    # Dữ liệu cần thiết để render form
    ngaycls = dao.get_remaining_days()
    cns = dao.load_object(ChuyenNganh)
    doctors = dao.load_bstrucca()

    return render_template('examine.html', chuyennganhs=cns, ngayconlai=ngaycls, doctors=doctors, loi=err_msg)

# @app.route("/api/doctors/<chuyennganh>", methods=['POST'])
# def api_doctors(chuyennganh):
#     try:
#         doctors = dao.load_bstrucca(int(chuyennganh))
#
#         # Chuyển đổi các đối tượng Row thành dictionary có thể tuần tự hóa JSON
#         doctors_list = []
#         for doctor in doctors:
#             doctors_list.append({
#                 "ten": doctor[0],
#                 "chuyennganh": doctor[1],
#                 "khoangthoigian": doctor[2],
#                 "khunggioid": doctor[3]
#             })
#
#         # Trả về kết quả chuỗi JSON hợp lệ
#         return jsonify(doctors_list), 200
#
#     except Exception as e:
#         print(f"[ERROR] Server error in api_doctors: {e}")  # Log chi tiết lỗi
#         return jsonify({"error": "Server error occurred", "details": str(e)}), 500

@app.route('/api/filter_doctors', methods=['POST'])
def filter_doctors():
    try:
        data = request.get_json()
        ngay = data.get('ngay')  # Ngày khám
        chuyennganh = data.get('chuyennganh')  # Chuyên ngành


        # Gọi hàm load_bstrucca để lấy danh sách bác sĩ
        doctors = dao.load_bstrucca(
            chuyennganh=int(chuyennganh) if chuyennganh else None,  # Nếu chuyennganh có thì chuyển thành số
            ngay=datetime.datetime.strptime(ngay, '%Y-%m-%d') if ngay else datetime.date.today()
        )

        # Chuẩn bị dữ liệu trả về
        doctors_list = []
        for doctor in doctors:
            doctors_list.append({
                "ten": doctor.bacsi_ten,
                "chuyennganh": doctor.chuyennganh_ten,
                "khoangthoigian": doctor.khunggio_ten,
                "khunggioid": doctor.khunggio_id
            })
        #
        # import pdb
        # pdb.set_trace()

        return jsonify(doctors_list), 200  # Trả về danh sách JSON với mã trạng thái OK

    except Exception as e:
        print(f'Lỗi khi xử lý filter_doctors: {e}')
        return jsonify({"error": "Lỗi khi xử lý filter_doctors", "details": str(e)}), 500

@app.route('/api/checksdt/<sdt>', methods=['POST'])
def api_check_sdt(sdt):
    try:
        # Kiểm tra độ dài số điện thoại
        if len(sdt) < 10:
            return jsonify({
                "error": "Bạn nhập chưa đủ 10 số"
            }), 400  # Trả về mã HTTP 400 (Bad Request)

        # Nếu số điện thoại hợp lệ (10 số hoặc hơn), thực hiện logic kiểm tra
        result, patient_info = dao.check_benhnhan(str(sdt))

        return jsonify({
            "result": result,
            "patient_info": patient_info
        }), 200  # Trả về mã HTTP 200 (OK)

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Trả về mã HTTP 500 nếu có lỗi khác

@app.route('/api/checkdanhsach/<ngay>', methods=['POST'])
def check_danh_sach_kham(ngay):
    try:
        # Gọi hàm tạo danh sách khám từ DAO
        phieu_dat_lich = dao.check_danhsachkham(ngay)

        # Trả về danh sách lọc được
        result = [{
            "ten": p.benhnhan.ten,
            "ngaydatlich": p.ngaydatlich.strftime('%d/%m/%Y'),
            "gioitinh": p.benhnhan.gioitinh,
            "ngaysinh": p.benhnhan.ngaysinh.strftime('%d/%m/%Y'),
            "sdt": p.benhnhan.sdt,
            "bacsikham": p.user.ten,
            "chuyennganh": p.user.chuyennganh.ten
        } for p in phieu_dat_lich]

        # import pdb
        # pdb.set_trace()

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask_login import current_user


@app.route('/api/taodanhsach/<ngay>', methods=['POST'])
def api_create_danhsachkham(ngay):
    """
    API tạo danh sách khám và liên kết các phiếu đặt lịch vào danh sách đó.
    """
    try:
        # Kiểm tra nếu người dùng chưa đăng nhập
        if not current_user.is_authenticated:
            return jsonify({"error": "Người dùng chưa đăng nhập!"}), 401

        # Lấy ID của người dùng từ current_user
        user_id = current_user.id

        # Gọi hàm xử lý từ DAO (file dao.py)
        dao.create_danhsachkham(user_id, ngay)

        return jsonify({
            "message": "Lập danh sách khám thành công!",
        }), 200

    except Exception as e:
        return jsonify({"error": f"Lỗi xảy ra: {str(e)}"}), 500

@app.route('/api/checkdanhsachhd/<ngay>', methods=['POST'])
def check_danh_sach_kham(ngay):
    try:
        # Gọi hàm tạo danh sách khám từ DAO
        phieu_dat_lich = dao.check_danhsachkham(ngay)

        # Trả về danh sách lọc được
        result = [{
            "ten": p.benhnhan.ten,
            "ngaydatlich": p.ngaydatlich.strftime('%d/%m/%Y'),
            "gioitinh": p.benhnhan.gioitinh,
            "ngaysinh": p.benhnhan.ngaysinh.strftime('%d/%m/%Y'),
            "sdt": p.benhnhan.sdt,
            "bacsikham": p.user.ten,
            "chuyennganh": p.user.chuyennganh.ten
        } for p in phieu_dat_lich]

        # import pdb
        # pdb.set_trace()

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask_login import current_user

@app.route("/login", methods=['GET', 'POST'])
def login_process():
    error=None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if not username or not password:
            error = "Username and password are required."
            return render_template('login.html', error=error)

        role = role.upper()

        # Xác thực người dùng và lấy thông tin vai trò
        u = dao.auth_user(username=username, password=password,role=role)
        if u:
            login_user(u)

            # Điều hướng dựa trên vai trò
            if role == 'ADMIN':
                return redirect('/admin')
            elif role == 'BACSI':
                return redirect('/admin')
            elif role == 'YTA':
                return redirect('/admin')
            elif role == 'THUNGAN':
                return redirect('/admin')
            else:
                return redirect('/')  # Trang mặc định nếu vai trò không khớp
        else:
            error = "Tên đăng nhập, mật khẩu hoặc vai trò không đúng."
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/login-admin', methods=['post'])
def login_admin_process():
    # username = request.form.get('username')
    # password = request.form.get('password')
    # u = dao.auth_user(username=username, password=password)
    # if u:
    #     login_user(u)
    #
    # return redirect('/admin')  # Điều hướng
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if not username or not password:
            error = "Username and password are required."
            return render_template('login.html', error=error)

        role = role.upper()

        # Xác thực người dùng và lấy thông tin vai trò
        u = dao.auth_user(username=username, password=password, role=role)
        if u:
            login_user(u)

            # Điều hướng dựa trên vai trò
            if role == 'ADMIN':
                return redirect('/admin')
            elif role == 'BACSI':
                return redirect('/admin')
            elif role == 'YTA':
                return redirect('/admin')
            elif role == 'THUNGAN':
                return redirect('/admin')
            else:
                return redirect('/')  # Trang mặc định nếu vai trò không khớp
        else:
            error = "Tên đăng nhập, mật khẩu hoặc vai trò không đúng."
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route("/logout")
def logout_process():
    logout_user() #Kết thúc phiên đăng nhập
    return redirect('/login') #Khi ấn vào logout, quay lại trang đăng nhập

@login.user_loader #Hàm này sẽ tự gọi khi hàm dưới chứng thực thành công
def get_user_by_id(user_id):
    return dao.get_user_by_id(user_id) #Flask login tự gọi

@app.route('/update-max-patients', methods=['POST'])
def update_max_patients():
    from flask import request, jsonify

    max_patients = request.form.get("maxPatients")

    if not max_patients:
        return jsonify({"success": False, "message": "Dữ liệu cần thiết không được gửi (maxPatients)."}), 400

    try:
        max_patients = int(max_patients)  # Chuyển đổi thành số nguyên
        if max_patients <= 0:
            return jsonify({"success": False, "message": "Giá trị phải lớn hơn 0!"}), 400

        app.config['SO_BENH_NHAN_TRONG_NGAY'] = max_patients  # Cập nhật vào cấu hình (hoặc lưu DB)

        return jsonify({
            "success": True,
            "message": "Cập nhật thành công!",
            "sobntoida": max_patients
        }), 200  # Mã HTTP thành công
    except ValueError:
        return jsonify({"success": False, "message": "Giá trị maxPatients không hợp lệ!"}), 400

@app.route('/update-price', methods=['POST'])
def update_price():
    from flask import request, jsonify

    new_price = request.form.get("price",type=int)

    if not new_price:
        return jsonify({"success": False, "message": "Dữ liệu cần thiết không được gửi (new_price)."}), 400
    try:
        new_price = int(new_price)  # Chuyển đổi thành số nguyên
        if new_price <= 1000:
            return jsonify({"success": False, "message": "Giá trị phải lớn hơn 1000!"}), 400

        app.config['SO_TIEN_KHAM'] = new_price  # Cập nhật vào cấu hình (hoặc lưu DB)
        formatted_price = f"{new_price:,}"
        return jsonify({
            "success": True,
            "message": "Cập nhật thành công!",
            "sotienkham": formatted_price
        }), 200  # Mã HTTP thành công
    except ValueError:
        return jsonify({"success": False, "message": "Giá trị maxPatients không hợp lệ!"}), 400

if __name__ == '__main__':
    from app import admin
    app.run(debug=True)




