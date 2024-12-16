//function updateDoctorsTable(obj){
//    value = obj.value
//    console.log(obj.value)
//    fetch(`/api/doctors/${value}`, {
//        method: 'POST',
//        headers: {
//            'Content-Type': 'application/json'
//        },
//        body: JSON.stringify({ chuyennganh: obj.value }) // Gửi JSON request
//    })
//    .then(response => response.json())
//    .then(data => {
//        console.log(data)
//        changeDoctorsTable(data);
//    })
//    .catch(error => {
//        console.error('Error fetching doctor data:', error);
//    });
//}

function updateDoctorsTable() {
    // Lấy giá trị ngày khám
    const selectedDateEl = document.querySelector('input[name="bnngaykham"]:checked'); // Lấy radio được chọn
    const selectedDate = selectedDateEl ? selectedDateEl.value : null; // Nếu có thì lấy giá trị, ngược lại null

    // Lấy giá trị chuyên ngành
    const selectedSpecialty = document.getElementById('chuyennganhSelect').value;

    // Kiểm tra nếu cả hai giá trị đều không được chọn
    if (!selectedDate && !selectedSpecialty) {
        console.warn('Vui lòng chọn ngày khám hoặc chuyên ngành');
        return;
    }

    // Chuẩn bị dữ liệu để gửi đến server
    const requestData = {
        ngay: selectedDate, // truyền ngày
        chuyennganh: selectedSpecialty // truyền chuyên ngành
    };

    console.log('Dữ liệu gửi lên server:', requestData);

    // Gửi request lên server
    fetch('/api/filter_doctors', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Danh sách bác sĩ được trả về:', data);
        changeDoctorsTable(data); // Cập nhật giao diện bảng bác sĩ
    })
    .catch(error => {
        console.error('Lỗi khi fetch bác sĩ:', error);
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
    const sdt = document.getElementById('bnphone').value; // Lấy giá trị số điện thoại

    fetch(`/api/checksdt/${sdt}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ sdt: sdt })
    })
    .then(response => {
        const statusDiv = document.getElementById('sdtstatus'); // Truy xuất div thông báo kết quả
        if (!response.ok) {
            // Nếu có lỗi HTTP (ví dụ: 400 hoặc 500)
            return response.json().then(data => {
                statusDiv.style.color = 'red';
                statusDiv.textContent = data.error; // Hiển thị lỗi trả về từ server
                throw new Error(data.error); // Ngừng tiếp tục xử lý
            });
        }
        return response.json(); // Nếu mọi thứ OK, tiếp tục để xử lý JSON
    })
    .then(data => {
        const statusDiv = document.getElementById('sdtstatus');

        if (data.patient_info) {
            // Điền thông tin tự động nếu tìm thấy bệnh nhân
            const patientInfo = data.patient_info;

            document.getElementById('bnname').value = patientInfo.ten || ''; // Điền tên
            document.getElementById('bnemail').value = patientInfo.email || ''; // Điền email

            const formattedDate = new Date(patientInfo.ngaysinh).toISOString().split('T')[0];
            document.getElementById('bnsinh').value = formattedDate; // Điền ngày sinh

            // Kiểm tra và đánh dấu giới tính
            document.getElementById(patientInfo.gioitinh === 'Nam' ? 'male' : 'female').checked = true;

            // Disable các trường đã điền
            document.getElementById('bnname').disabled = true;
            document.getElementById('bnemail').disabled = true;
            document.getElementById('bnsinh').disabled = true;
            document.getElementById('male').disabled = true;
            document.getElementById('female').disabled = true;

            statusDiv.style.color = 'green';
            statusDiv.textContent = `Thông tin đã được điền tự động`;
        } else {
            // Nếu không tìm thấy thông tin bệnh nhân
            statusDiv.style.color = 'red';
            statusDiv.textContent = `Vui lòng nhập thông tin cho lần khám đầu tiên`;
        }
    })
    .catch(error => {
        console.error('Error:', error); // Log lỗi vào console (để debug)
    });
}