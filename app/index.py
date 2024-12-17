from flask import render_template, request, redirect, session, jsonify
from app import app, login

import dao
from flask_login import login_user, logout_user #Ghi nhận trạng thái login, logout của session (Một phiên)


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/examine")
def examine():
    return render_template('examine.html')

@app.route("/login", methods=['get', 'post']) #Đường dẫn web login, mặc định chỉ đang nhận 'get', không nhận 'post'
def login_process():
    if request.method.__eq__('POST'): #Kiểm tra xem request gửi lên là get hay post
        username = request.form.get('username')
        password = request.form.get('password')
        u = dao.auth_user(username = username, password = password)
        if u:
            login_user(u)
            return redirect('/') #Điều hướng

    return render_template('login.html') #Get là dùng để truy cập vào trang, post thì sẽ xử lý login, đây là phản hồi về template

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




