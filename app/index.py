from flask import render_template, request, redirect, session, jsonify
from app import app, login

import dao, json
from flask_login import login_user, logout_user #Ghi nhận trạng thái login, logout của session (Một phiên)

from app.dao import count_so_phan_tu
from app.models import ChuyenNganh


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/examine", methods=['GET','POST'])
def examine():
    if request.method.__eq__('POST'): #Kiểm tra xem request gửi lên là get hay post
        tenbn = request.form.get('bnname')
        sdtbn = request.form.get('bnphone')
        emailbn = request.form.get('bnemail')
        sinhbn = request.form.get('bnsinh')
        gioibn = request.form.get('bngioi')
        trieuchungbn = request.form.get('bntrieuchung')
        lichkhambn = request.form.get('bnlichkham')

    ngaycls = dao.get_remaining_days()
    cns = dao.load_object(ChuyenNganh)
    doctors = dao.load_bstrucca()
    return render_template('examine.html', chuyennganhs = cns, ngayconlai = ngaycls, doctors = doctors)

@app.route("/api/doctors/<chuyennganh>", methods=['POST'])
def api_doctors(chuyennganh):
    try:
        doctors = dao.load_bstrucca(int(chuyennganh))

        # Chuyển đổi các đối tượng Row thành dictionary có thể tuần tự hóa JSON
        doctors_list = []
        for doctor in doctors:
            doctors_list.append({
                "ten": doctor[0],
                "chuyennganh": doctor[1],
                "khoangthoigian": doctor[2],
            })

        # Trả về kết quả chuỗi JSON hợp lệ
        return jsonify(doctors_list), 200

    except Exception as e:
        print(f"[ERROR] Server error in api_doctors: {e}")  # Log chi tiết lỗi
        return jsonify({"error": "Server error occurred", "details": str(e)}), 500

@app.route('/api/checksdt/<sdt>', methods=['POST'])
def api_check_sdt(sdt):
    try:
        # Kiểm tra thông tin bệnh nhân
        result, patient_info = dao.check_benhnhan(str(sdt))
        return {
            "result": result,
            "patient_info": patient_info
        }

    except Exception as e:
        return {"error": str(e)}, 500

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

if __name__ == '__main__':
    from app import admin
    app.run(debug=True)




