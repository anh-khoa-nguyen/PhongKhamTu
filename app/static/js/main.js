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
    document.addEventListener('DOMContentLoaded', function () {
     // Lấy giá trị ngày khám
        console.log(ok)
        const radioButtons = document.getElementsByName("bnngaykham");
        const selectedDate = selectedDateEl ? selectedDateEl.value : null; // Nếu có thì lấy giá trị, ngược lại null

        console.log(selectedDateEl)



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
    })
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


document.getElementById('ten').addEventListener('input', function() {
        // Lấy tất cả các option trong datalist
        var patientsOptions = document.querySelectorAll('#patients option');

        // Tìm bệnh nhân có tên giống với giá trị người dùng nhập vào
        var selectedOption = Array.from(patientsOptions).find(function(option) {
            return option.value === document.getElementById('ten').value;
        });

        // Nếu tìm thấy bệnh nhân, lấy ID và ngày sinh
        if (selectedOption) {
            var patientId = selectedOption.getAttribute('data-id');
            var dob = selectedOption.getAttribute('data-dob');
            var phone = selectedOption.getAttribute('data-phone');
            // Định dạng lại ngày sinh (ví dụ từ YYYY-MM-DD sang DD-MM-YYYY)
            var formattedDob = formatDate(dob);

            // Gán giá trị vào input DOB
            document.getElementById('DOB').value = formattedDob;
            document.getElementById('PatientId').value = patientId;  // Lưu PatientId vào hidden input
            document.getElementById('Numberphone').value = phone;
        }
    });
function formatDate(dateStr) {
        var date = new Date(dateStr); // Chuyển đổi chuỗi ngày thành đối tượng Date
        var day = ("0" + date.getDate()).slice(-2);  // Lấy ngày và đảm bảo có 2 chữ số
        var month = ("0" + (date.getMonth() + 1)).slice(-2);  // Lấy tháng và đảm bảo có 2 chữ số
        var year = date.getFullYear();  // Lấy năm
        return day + '-' + month + '-' + year;  // Trả về ngày theo định dạng DD-MM-YYYY

    }


function autoGenerate() {
    const tableBody = document.getElementById('tableBody');
    const rowIndex = tableBody.children.length + 1; // Chỉ số dòng mới

    // Tạo một dòng mới
    const newRow = document.createElement('tr');

    // Tạo cột STT
    const indexCell = document.createElement('td');
    indexCell.classList.add('text-center');
    indexCell.textContent = rowIndex;
    newRow.appendChild(indexCell);

    // Tạo cột chọn tên thuốc
    const drugInputCell = document.createElement('td');
    drugInputCell.classList.add('text-center');
    const drugInput = document.createElement('input');
    drugInput.setAttribute('list', 'drugsList');
    drugInput.classList.add('form-control', 'border-0');
    drugInput.setAttribute('required', '');
    drugInput.setAttribute('autocomplete', 'off');
    drugInput.setAttribute('id', 'drugInput_' + rowIndex);
    drugInputCell.appendChild(drugInput);
    newRow.appendChild(drugInputCell);

    // Tạo cột đơn vị
    const unitCell = document.createElement('td');
    unitCell.classList.add('text-center');
    const unitInput = document.createElement('input');
    unitInput.setAttribute('type', 'text');
    unitInput.classList.add('form-control', 'border-0');
    unitInput.setAttribute('readonly', 'true');
    unitInput.setAttribute('id', 'unitInput_' + rowIndex);
    unitCell.appendChild(unitInput);
    newRow.appendChild(unitCell);

    // Tạo cột số lượng
    const quantityCell = document.createElement('td');
    quantityCell.classList.add('text-center');
    const quantityInput = document.createElement('input');
    quantityInput.setAttribute('type', 'number');
    quantityInput.classList.add('form-control', 'border-0');
    quantityInput.setAttribute('value', 1);
    quantityInput.setAttribute('min', 1);
    quantityInput.setAttribute('id', 'quantityInput_' + rowIndex);
    quantityCell.appendChild(quantityInput);
    newRow.appendChild(quantityCell);

    // Tạo cột tồn kho
    const stockCell = document.createElement('td');
    stockCell.classList.add('text-center');
    const stockInput = document.createElement('input');
    stockInput.setAttribute('type', 'text');
    stockInput.classList.add('form-control', 'border-0');
    stockInput.setAttribute('readonly', 'true');
    stockInput.setAttribute('id', 'stockInput_' + rowIndex);
    stockCell.appendChild(stockInput);
    newRow.appendChild(stockCell);

    // Tạo cột giá
    const priceCell = document.createElement('td');
    priceCell.classList.add('text-center');
    const priceInput = document.createElement('input');
    priceInput.setAttribute('type', 'text');
    priceInput.classList.add('form-control', 'border-0');
    priceInput.setAttribute('readonly', 'true');
    priceInput.setAttribute('id', 'priceInput_' + rowIndex);
    priceCell.appendChild(priceInput);
    newRow.appendChild(priceCell);

    // Tạo cột tổng cộng
    const totalCell = document.createElement('td');
    totalCell.classList.add('text-center');
    const totalInput = document.createElement('input');
    totalInput.setAttribute('type', 'text');
    totalInput.classList.add('form-control', 'border-0');
    totalInput.setAttribute('readonly', 'true');
    totalInput.setAttribute('id', 'totalInput_' + rowIndex);
    totalCell.appendChild(totalInput);
    newRow.appendChild(totalCell);

    // Tạo cột nút xóa
    const deleteCell = document.createElement('td');
    deleteCell.classList.add('text-center');
    const deleteButton = document.createElement('button');
    deleteButton.classList.add('btn', 'rounded-circle', 'btn-danger');
    deleteButton.innerHTML = '<i class="bi bi-x ">X</i>';
    deleteButton.onclick = function () {
        tableBody.removeChild(newRow); // Xóa dòng hiện tại
        updateRowIndexes(); // Cập nhật lại STT
    };
    deleteCell.appendChild(deleteButton);
    newRow.appendChild(deleteCell);

    // Thêm dòng mới vào bảng
    tableBody.appendChild(newRow);


    // Lắng nghe sự kiện 'input' trên drugInput
    drugInput.addEventListener('input', function () {
    const selectedDrug = drugInput.value; // Lấy giá trị đã chọn từ drugInput
        const drugsOptions = document.querySelectorAll('#drugsList option');
        const selectedOption = Array.from(drugsOptions).find(option => option.value === selectedDrug);

        if (selectedOption) {
            const unit = selectedOption.dataset.unit;
            const stock = selectedOption.dataset.quantity;
            const price = selectedOption.dataset.price;

            // Cập nhật các input trong dòng
            unitInput.value = unit;
            stockInput.value = stock;
            priceInput.value = price;

            // Tính tổng cộng
            totalInput.value = price * quantityInput.value; // Tổng cộng = giá * số lượng
        }
    });

    // Lắng nghe sự kiện thay đổi số lượng để tính lại tổng cộng
    quantityInput.addEventListener('input', function () {
        const price = parseFloat(priceInput.value) || 0;
        const quantity = parseInt(quantityInput.value) || 1;
        totalInput.value = price * quantity; // Tính lại tổng cộng
    });

    // Hàm cập nhật lại STT
    function updateRowIndexes() {
        document.querySelectorAll('#tableBody tr').forEach((row, index) => {
            row.querySelector('td:first-child').textContent = index + 1;
        });
    }
}

 function calculateTotal() {
        let totalSum = 0;
        const totalInputs = document.querySelectorAll('[id^="totalInput_"]');
        totalInputs.forEach(function (input) {
            const value = parseFloat(input.value) || 0;
            totalSum += value;
            console.log("tổng cộng:",totalSum)
        });

        // Cập nhật tổng số tiền cần thanh toán
        const allTotal = document.getElementById('AllTotal');

         document.getElementById("AllTotal").value = totalSum;
    }
    function onRowInputChange() {
    // Lắng nghe sự thay đổi trên tất cả các ô nhập liệu trong bảng (cả input số lượng và các ô nhập liệu khác)
    const tableBody = document.getElementById('tableBody');

    tableBody.addEventListener('input', function(event) {
        const target = event.target;

        // Kiểm tra xem sự kiện có xảy ra trên các ô nhập liệu liên quan đến thuốc, số lượng, giá, v.v.
        if (target.closest('tr')) {
            // Gọi hàm tính tổng cộng
            calculateTotal();
        }
    });
}
function calculateTotal() {
    let totalSum = 0;
    const totalInputs = document.querySelectorAll('[id^="totalInput_"]'); // Lọc tất cả các ô có id bắt đầu bằng "totalInput_"

    totalInputs.forEach(function (input) {
        const value = parseFloat(input.value) || 0;
        totalSum += value;
    });

    // Cập nhật tổng số tiền cần thanh toán vào ô input có id là "AllTotal"
    const allTotal = document.getElementById('AllTotal');
    const formattedTotal = totalSum.toLocaleString('en-US');
    allTotal.value = totalSum;

    // In tổng số tiền ra console để kiểm tra
//    console.log("Tổng cộng:", totalSum);
}

// Gọi hàm khi trang được tải
window.onload = function() {
    onRowInputChange(); // Lắng nghe sự thay đổi trong bảng và tính tổng cộng khi có sự thay đổi
};