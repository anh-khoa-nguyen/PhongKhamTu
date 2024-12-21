from flask import render_template, request, redirect, session, jsonify
from app import app, login

import dao
from flask_login import login_user, logout_user #Ghi nhận trạng thái login, logout của session (Một phiên)

from app.dao import count_so_phan_tu
from app.models import ChuyenNganh


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/examine", methods=['POST', 'GET'])
def examine():
    if request.method.__eq__('POST'):
        data = request.get_json()  # Get the JSON data from the request
        chuyennganh = data.get('chuyennganh')  # Get the 'chuyennganh' value
        doctors = dao.load_bacsi(chuyennganh)  # Call the DAO function with the selected specialization

        # Format doctors and return as JSON
        doctor_list = [
            {
                "User": {"id": doctor.User.id, "ten": doctor.User.ten},  # Replace fields based on your model structure
                "ChuyenNganh": {"id": doctor.ChuyenNganh.id, "ten": doctor.ChuyenNganh.ten}
            }
            for doctor in doctors
        ]
        return jsonify(doctors=doctor_list)  # Return the filtered doctors as a JSON response

    ngaycls = dao.get_remaining_days()


    cns = dao.load_object(ChuyenNganh)
    return render_template('examine.html', chuyennganhs = cns, ngayconlai = ngaycls)

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




