function updateDoctorsTable(obj){
    value = obj.value
    console.log(obj.value)
    fetch(`/api/doctors/${value}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ chuyennganh: obj.value }) // Gửi JSON request
    })
    .then(response => response.json())
    .then(data => {
        console.log(data)
        changeDoctorsTable(data);
    })
    .catch(error => {
        console.error('Error fetching doctor data:', error);
    });
}

function changeDoctorsTable(data){
    console.log(data)
    const tableBody = document.querySelector('#doctorTable tbody'); // Truy xuất tbody của bảng
    tableBody.innerHTML = '';

    if (data) {
        data.forEach((doctor, index) => {
            // Tạo một hàng (row) mới với các thông tin được trả về
            const row = `
                <tr>
                    <td>${index + 1}</td>
                    <td>${doctor.ten}</td>
                    <td>${doctor.chuyennganh}</td>
                    <td>${doctor.khoangthoigian}</td>
                    <td><input type="radio" name="doctor" value=""></td>
                </tr>
            `;
            // Thêm hàng mới vào bảng
            tableBody.innerHTML += row;
        });
    } else {
        // Trường hợp không có bác sĩ phù hợp
        tableBody.innerHTML = `<tr><td colspan="5">Không có bác sĩ phù hợp</td></tr>`;
    }
}

function checkSDT() {
    const sdt = document.getElementById('sdtcheck').value; // Lấy giá trị số điện thoại

    fetch(`/api/checksdt/${sdt}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ sdt: sdt })
    })
    .then(response => response.json())
    .then(data => {
        const statusDiv = document.getElementById('sdtstatus'); // Truy xuất div thông báo kết quả

        if (data.patient_info) {
            // Điền thông tin tự động nếu tìm thấy bệnh nhân
            const patientInfo = data.patient_info;

            document.getElementById('bnname').value = patientInfo.ten || ''; // Điền tên
            document.getElementById('bnemail').value = patientInfo.email || ''; // Điền email

            // Chuyển đổi ngày sinh sang định dạng YYYY-MM-DD

            const formattedDate = new Date(patientInfo.ngaysinh).toISOString().split('T')[0]; // Tách phần "YYYY-MM-DD"
            document.getElementById('bnsinh').value = formattedDate; // Điền ngày sinh

            // Kiểm tra và đánh dấu giới tính
            if (patientInfo.gioitinh === 'Nam') {
                document.getElementById('male').checked = true;
            } else if (patientInfo.gioitinh === 'Nữ') {
                document.getElementById('female').checked = true;
            }

            // Disable các trường đã điền
            document.getElementById('bnname').disabled = true;
            document.getElementById('bnemail').disabled = true; // Disable email
            document.getElementById('bnsinh').disabled = true;
            document.getElementById('male').disabled = true;
            document.getElementById('female').disabled = true;

            statusDiv.style.color = 'green';
            statusDiv.textContent = `Thông tin đã được điền tự động`;
        } else {
            // Thông báo không tìm thấy thông tin bệnh nhân
            statusDiv.style.color = 'red';
            statusDiv.textContent = `Vui lòng nhập thông tin cho lần khám đầu tiên`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const statusDiv = document.getElementById('status'); // Khu vực hiển thị lỗi
        statusDiv.style.color = 'red';
        statusDiv.textContent = 'Có lỗi xảy ra khi kiểm tra số điện thoại.';
    });
}