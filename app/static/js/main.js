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
    const radioNgayKham = document.querySelector('input[name="bnngaykham"]:checked');
    const ngaykham = radioNgayKham ? radioNgayKham.value : null; // Nếu có thì lấy giá trị, ngược lại null

    // Lấy giá trị chuyên ngành
    const chuyennganh = document.getElementById('chuyennganhSelect').value;

    // Kiểm tra nếu cả hai giá trị đều không được chọn
    if (!radioNgayKham) {
        console.warn('Vui lòng chọn ngày khám hoặc chuyên ngành');
        return;
    }

    // Chuẩn bị dữ liệu để gửi đến server
    const requestData = {
        ngay: ngaykham, // truyền ngày
        chuyennganh: chuyennganh // truyền chuyên ngành
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
                    <td><input type="radio" name="bnbacsi_giokham" value="${doctor.ten}|${doctor.khunggioid}"></td>
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

            //Disable các trường đã điền
            document.getElementById('bnname').setAttribute('readonly', 'readonly');
            document.getElementById('bnemail').setAttribute('readonly', 'readonly');
            document.getElementById('bnsinh').setAttribute('readonly', 'readonly');
            // Đặt radio buttons thành "read-only" bằng cách ngăn sự kiện click
            document.getElementById('male').addEventListener('click', function(event) {
                event.preventDefault(); // Ngăn không cho thực hiện thay đổi
            });

            document.getElementById('female').addEventListener('click', function(event) {
                event.preventDefault(); // Ngăn không cho thực hiện thay đổi
            });

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

function handleChon() {
    const dateInput = document.getElementById("chonngay");
    const selectedDate = dateInput.value;

    if (!selectedDate) {
        alert("Vui lòng chọn ngày trước khi tiếp tục!");
        return;
    }

    fetch(`/api/checkdanhsach/${selectedDate}`, { method: "POST" })
        .then(response => response.json())
        .then(data => {
            renderDanhSachKham(data);
        })
        .catch(error => {
            console.error("Lỗi khi gửi yêu cầu đến API:", error);
        });
}

// Hàm render danh sách khám
function renderDanhSachKham(data) {
    const tableBody = document.querySelector("table tbody");
    const createListButton = document.getElementById("createListButton"); // ID nút "Lập danh sách"

    // Xóa dữ liệu cũ
    tableBody.innerHTML = "";

    if (data && data.length > 0) {
        // Thêm dữ liệu mới vào bảng
        data.forEach((item, index) => {
            const row = `
                <tr>
                    <td>${index + 1}</td>
                    <td>${item.ten}</td>
                    <td>${item.ngaydatlich}</td>
                    <td>${item.gioitinh === 0 ? 'Nam' : 'Nữ'}</td>
                    <td>${item.ngaysinh}</td>
                    <td>${item.sdt}</td>
                    <td>${item.bacsikham}</td>
                    <td>${item.chuyennganh}</td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });

        createListButton.classList.remove("btn-secondary");
        createListButton.classList.add("btn-primary");
        createListButton.disabled = false; // Bật nút
    } else {
        // Trường hợp không có dữ liệu
        tableBody.innerHTML = `<tr><td colspan="8">Không có dữ liệu hợp lệ</td></tr>`;

        // Nếu không có dữ liệu, làm nút "Lập danh sách" bị vô hiệu hóa
        if (createListButton) {
            createListButton.classList.remove("btn-primary");
            createListButton.classList.add("btn-secondary");
            createListButton.disabled = true;
        }
    }
}

function handleChon2() {
    const dateInput = document.getElementById("chonngay2");
    const selectedDate = dateInput.value;

    if (!selectedDate) {
        alert("Vui lòng chọn ngày trước khi tiếp tục!");
        return;
    }

    fetch(`/api/checkdanhsachhd/${selectedDate}`, { method: "POST" })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            renderDanhSachHD(data);
        })
        .catch(error => {
            console.error("Lỗi khi gửi yêu cầu đến API:", error);
        });
}

function renderDanhSachHD(data) {
    const tableBody = document.querySelector("table tbody"); // Lấy `<tbody>` của bảng
    const createListButton = document.getElementById("createListButton"); // Nút "Lập danh sách" nếu có

    // Xóa nội dung cũ trong bảng
    tableBody.innerHTML = "";

    console.log(data)
    if (data && data.length > 0) {
        data.forEach((item, index) => {
            // Tạo một hàng `<tr>` mới với thông tin hóa đơn
            const row = `
                <tr>
                    <td class="text-center">${item.id}</td>
                    <td class="text-center">${item.ngaykham}</td>
                    <td class="text-center">${item.giakham.toLocaleString()} VND</td>
                    <td class="text-center">${item.ten}</td>
                    <td class="text-center">${item.gioitinh === false ? 'Nam' : 'Nữ'}</td>
                    <td class="text-center">${item.ngaysinh}</td>
                    <td class="text-center">${item.tienthuoc.toLocaleString()} VND</td>
                    <td class="text-center">
                        ${
                            item.isThanhtoan
                                ? `<button class="btn btn-success" disabled>Đã Thanh Toán</button>`
                                : `<button
                                    class="btn btn-danger thanh-toan-btn"
                                    data-toggle="modal"
                                    data-target="#exampleModal"
                                    onclick="load_chitiethoadon(${item.id})">
                                    Chưa Thanh Toán
                                  </button>`
                        }
                    </td>
                </tr>
            `;
            // Gắn hàng vào bảng
            tableBody.innerHTML += row;
        });

    } else {
        // Nếu không có dữ liệu hóa đơn
        tableBody.innerHTML = `
            <tr>
                <td class="text-center" colspan="8">Không có hóa đơn hợp lệ</td>
            </tr>
        `;
    }
}

function disableChonNgay() {
    const createListButton = document.getElementById("createListButton"); // Nút "Lập danh sách"

    // Nếu nút đang là enabled với class btn-primary
    createListButton.classList.remove("btn-primary");
    createListButton.classList.add("btn-secondary");
    createListButton.disabled = true; // Tắt nút
}

async function createDanhSachKham() {
        try {
            const ngay = document.getElementById("chonngay").value; // Lấy ngày từ input chọn

            if (!ngay) {
                alert("Vui lòng chọn ngày!");
                return;
            }

            // Gọi API để lập danh sách khám
            const response = await fetch(`/api/taodanhsach/${ngay}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ ngay }), // Gửi ngày cần lập danh sách khám
            });

            const result = await response.json();

            if (response.status === 200) {
                alert("Lập danh sách khám thành công!");

                console.log(result); // Xem dữ liệu trả về
                location.reload(); // Reload lại trang để cập nhật
            } else {
                alert(result.error || "Lỗi xảy ra khi lập danh sách khám!");
            }
        } catch (error) {
            console.error("Lỗi khi tạo danh sách khám:", error);
            alert("Lỗi không xác định!");
        }
    }

    // Thêm sự kiện onclick vào nút "Lập danh sách"
    document.getElementById("createListButton").onclick = createDanhSachKham;

async function load_chitiethoadon(hoadonId) {
    try {
        // Gọi API lấy dữ liệu hóa đơn từ server
        const response = await fetch(`/api/hoadon/${hoadonId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Không thể tải chi tiết hóa đơn');
        }

        const hoadon = await response.json(); // Lấy dữ liệu JSON từ API

        // Gọi hàm load_hoadon với dữ liệu chi tiết hóa đơn (chitiet = true)
        load_hoadon(hoadon, true);
    } catch (error) {
        console.error('Lỗi khi tải chi tiết hóa đơn:', error);
    }
}

function load_hoadon(hoadon, chitiet = false) {
    if (!hoadon) {
        console.error('Không có dữ liệu hóa đơn để hiển thị');
        return;
    }

    // Hiển thị thông tin hóa đơn lên modal (giả sử bạn dùng các ID trong HTML để hiển thị)
    document.getElementById('modal-mahoadon').textContent = hoadon.id;
    document.getElementById('modal-tenkhachhang').textContent = hoadon.ten;
    document.getElementById('modal-sdt').textContent = hoadon.sdt;
    document.getElementById('modal-tongtien').textContent = `${(hoadon.value + hoadon.gia_kham).toLocaleString()} VND`;
    document.getElementById('modal-ngaysinh').textContent = new Date(hoadon.ngaysinh).toISOString().split('T')[0];
    document.getElementById('modal-ngaykham').textContent = new Date(hoadon.ngaykham).toISOString().split('T')[0];
    const thanhtoanbtn = document.getElementById("thanhtoanbtn");
    thanhtoanbtn.setAttribute('data-hoadonid', '');
    thanhtoanbtn.setAttribute('data-hoadonid', `${hoadon.id}`);

    if (chitiet && hoadon.chitiet) {
        const tableBody = document.getElementById('tableBody');
        tableBody.innerHTML = ''; // Xóa dữ liệu cũ trong bảng
        hoadon.chitiet.forEach((item, index) => {
            const totalPrice = item.gia * item.soluongthuoc;
            const row = `
                <tr>
                    <td class="text-center">${index + 1}</td>
                    <td class="text-center">${item.tenthuoc}</td>
                    <td class="text-center">${item.soluongthuoc}</td>
                    <td class="text-center">${item.gia.toLocaleString()} VND</td>
                    <td class="text-center">${totalPrice.toLocaleString()} VND</td>
                </tr>
            `;
            tableBody.innerHTML += row; // Thêm dòng vào bảng
        });
    }
}

function confirmthanhtoan(button) {
    const hoadonId = button.getAttribute("data-hoadonid");

    if (!hoadonId) {
        alert("Không tìm thấy mã hóa đơn!");
        return;
    }

    const userConfirmation = confirm("Bạn có chắc chắn rằng hóa đơn này đã được thanh toán?");

    if (userConfirmation) {
        // Gửi PUT request tới API
        fetch(`/api/thanhtoan/${hoadonId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then(response => {
                if (response.ok) {
                    // Thông báo thành công
                    alert("Hóa đơn đã được cập nhật sang trạng thái ĐÃ THANH TOÁN.");
                    location.reload(); // Reload lại trang để cập nhật trạng thái
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.message) {
                    alert(`Lỗi: ${data.message}`);
                }
            })
            .catch(error => {
                console.error("Lỗi khi gửi yêu cầu:", error);
                alert("Có lỗi xảy ra, vui lòng thử lại!");
            });
    }
}

function confirmthanhtoan(button) {
    const hoadonId = button.getAttribute("data-hoadonid");

    if (!hoadonId) {
        alert("Không tìm thấy mã hóa đơn!");
        return;
    }

    const xacnhan = confirm("Bạn có chắc chắn rằng hóa đơn này đã được thanh toán?");

    if (xacnhan) {
        // Gửi PUT request tới API
        fetch(`/api/thanhtoan/${hoadonId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
        })
            .then(response => {
                if (response.ok) {
                    // Thông báo thành công
                    alert("Hóa đơn đã được cập nhật sang trạng thái ĐÃ THANH TOÁN.");
                    location.reload(); // Reload lại trang để cập nhật trạng thái
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.message) {
                    alert(`Lỗi: ${data.message}`);
                }
            })
            .catch(error => {
                console.error("Lỗi khi gửi yêu cầu:", error);
                alert("Có lỗi xảy ra, vui lòng thử lại!");
            });
    }
}

// Hiển thị lịch sử khám bệnh của bệnh nhân
function xemlichsukham(button) {
    const benhnhanId = button.getAttribute('data-benhnhanid');

    if (!benhnhanId) {
        console.error("Không có ID bệnh nhân!");
        return;
    }

    // Gọi đến API lấy danh sách lịch sử khám
    fetch(`/api/lichsubenh/${benhnhanId}`)
        .then(response => response.json())
        .then(data => {
            if (!data || data.length === 0) {
                alert("Không tìm thấy lịch sử khám!");
                return;
            }

            // Hiển thị thông tin bệnh nhân trong modal
            document.getElementById('modal-tenbn').innerText = data[0].tenbenhnhan;
            document.getElementById('modal-ngaysinhbn').innerText = data[0].ngaysinhbenhnhan;

            // Hiển thị danh sách lịch sử khám
            const tableBody = document.querySelector('#exampleModal #tableBody');
            tableBody.innerHTML = ''; // Xóa nội dung cũ

            data.forEach((item, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="text-center">${index + 1}</td>
                    <td class="text-center">${item.ngaykham}</td>
                    <td class="text-center">${item.chuandoan}</td>
                    <td class="text-center">
                        <button class="btn btn-success btn-sm" onclick="xemChiTietDonThuoc(${item.phieukhambenh_id})">
                            Xem chi tiết
                        </button>
                    </td>`;
                tableBody.appendChild(row);
            });

            // Hiển thị modal
            $('#exampleModal').modal('show');
        })
        .catch(error => {
            console.error("Có lỗi xảy ra khi lấy lịch sử khám:", error);
            alert("Không thể tải lịch sử khám!");
        });
}

// Xem chi tiết đơn thuốc của phiếu khám
function xemChiTietDonThuoc(phieukhambenhId) {
    if (!phieukhambenhId) {
        console.error("Không tìm thấy ID phiếu khám bệnh!");
        return;
    }

    // Gọi API lấy chi tiết đơn thuốc
    fetch(`/api/chitietdonthuoc/${phieukhambenhId}`)
        .then(response => response.json())
        .then(data => {
            if (!data || data.length === 0) {
                alert("Không có chi tiết đơn thuốc!");
                return;
            }

            // Hiển thị chi tiết đơn thuốc lên bảng trong form chính
            const tableBody = document.getElementById('tableBodyy');
            tableBody.innerHTML = ''; // Xóa dữ liệu cũ

            data.chitiet.forEach((item, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="text-center">${index + 1}</td>
                    <td class="text-center">${item.tenthuoc}</td>
                    <td class="text-center">${item.donvitinh}</td>
                    <td class="text-center">${item.soluong}</td>
                    <td class="text-center">${item.trongkho}</td>
                    <td class="text-center">${item.gia.toLocaleString()}</td>
                    <td class="text-center">${item.tongcong.toLocaleString()}</td>`;
                tableBody.appendChild(row);
            });

            document.getElementById("Total").value = data.tong_tien;
            document.getElementById('add-row-btn').remove();
            // Ẩn modal lịch sử khám
            $('#exampleModal').modal('hide');
        })
        .catch(error => {
            console.error("Có lỗi xảy ra khi lấy chi tiết đơn thuốc:", error);
            alert("Không thể tải chi tiết đơn thuốc!");
        });
}

































//Mi
function checkName_Day_Sdt() {
    // Lấy giá trị từ input có id là "ten"
    const inputElement = document.getElementById("ten");
    const patientName = inputElement.value; // Lấy tên bệnh nhân từ input

    // Tìm id của bệnh nhân từ datalist
    const patientOption = Array.from(document.querySelectorAll('#patients option')).find(option => option.value === patientName);

    const patientId = patientOption ? patientOption.id : null; // Lấy id của bệnh nhân nếu tìm thấy

    // Cập nhật vào input hidden nếu có id
    if (patientId) {
        console.log("Patient ID found:", patientId);
        document.getElementById("PatientId").value = patientId;
            document.getElementById("btnHistory").setAttribute('data-benhnhanid',`${patientOption.id}`)
    document.getElementById("btnHistory").disabled = false
    } else {
        // Nếu không tìm thấy id, xóa giá trị trong input hidden
        document.getElementById("PatientId").value = '';
    }

    // Kiểm tra xem patientId có tồn tại hay không trước khi gửi API
   if (patientId) {
        // Gửi yêu cầu đến API với patientId
        fetch(`/api/checkName_Day_Sdt/${patientId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: patientId }) // Truyền id bệnh nhân
        })
        .then(response => {
            if (!response.ok) { // Kiểm tra mã trạng thái không phải là 2xx
                return response.json().then(data => {
                    // Hiển thị lỗi nếu có
                    const statusDiv = document.getElementById("statusDiv");
                    statusDiv.style.color = 'red';
                    statusDiv.textContent = data.error || 'An error occurred';
                    throw new Error(data.error || 'Error without message');
                });
            }
            return response.json(); // Trả về dữ liệu JSON nếu thành công
        })
        .then(data => {
            console.log("Data received from API:", data);
             if (data.patient_info.ngaysinh) {
        // Định dạng lại ngày sinh từ chuỗi hoặc đối tượng Date
        let ngaysinh = new Date(data.patient_info.ngaysinh);

        // Kiểm tra xem ngaysinh có hợp lệ không
        if (!isNaN(ngaysinh)) {
            // Định dạng ngày theo dạng dd/mm/yyyy
            let day = String(ngaysinh.getDate()).padStart(2, '0');
            let month = String(ngaysinh.getMonth() + 1).padStart(2, '0'); // Lưu ý tháng bắt đầu từ 0
            let year = ngaysinh.getFullYear();

            // Cập nhật giá trị vào ô DOB với định dạng dd/mm/yyyy
            document.getElementById("DOB").value = `${day}/${month}/${year}`;
            document.getElementById("Numberphone").value = data.patient_info.sdt || "";
        }
        }})
        .catch(error => {
            console.error("Error occurred in fetch request:", error);

            // Kiểm tra các lỗi mạng
            if (error.response) {
                console.error("API Response Error:", error.response);
            } else if (error.request) {
                console.error("No response received:", error.request);
            } else {
                console.error("General Error:", error.message);
            }
        });
    } else {
        console.error("Patient ID not found.");
    }
};



function formatDate(dateStr) {
        var date = new Date(dateStr); // Chuyển đổi chuỗi ngày thành đối tượng Date
        var day = ("0" + date.getDate()).slice(-2);  // Lấy ngày và đảm bảo có 2 chữ số
        var month = ("0" + (date.getMonth() + 1)).slice(-2);  // Lấy tháng và đảm bảo có 2 chữ số
        var year = date.getFullYear();  // Lấy năm
        return day + '-' + month + '-' + year;  // Trả về ngày theo định dạng DD-MM-YYYY

    }






function autoGenerate() {
if (event) {
        event.preventDefault();
    }
    const tableBodyy = document.getElementById('tableBodyy');
    const rowIndex = tableBodyy.children.length + 1; // Chỉ số dòng mới

    // Tạo một dòng mới
    const newRow = document.createElement('tr');

    // Cột STT
    const indexCell = document.createElement('td');
    indexCell.classList.add('text-center');
    indexCell.textContent = rowIndex;
    newRow.appendChild(indexCell);

    // Cột chọn tên thuốc
    const drugInputCell = document.createElement('td');
    drugInputCell.classList.add('text-center');
    const drugInput = document.createElement('input');
    drugInput.setAttribute('list', 'drugsList');
    drugInput.classList.add('form-control', 'border-0');
    drugInput.setAttribute('form', 'form-pkb');
    drugInput.setAttribute('required', '');
    drugInput.setAttribute('autocomplete', 'off');
    drugInput.setAttribute('id', `drugInput_${rowIndex}`);
    drugInputCell.appendChild(drugInput);
    newRow.appendChild(drugInputCell);

    // Cột đơn vị
    const unitCell = document.createElement('td');
    unitCell.classList.add('text-center');
    const unitInput = document.createElement('input');
    unitInput.setAttribute('type', 'text');
    unitInput.classList.add('form-control', 'border-0');
    unitInput.setAttribute('readonly', 'true');
    unitInput.setAttribute('id', `unitInput_${rowIndex}`);
    unitCell.appendChild(unitInput);
    newRow.appendChild(unitCell);

    // Cột số lượng
    const quantityCell = document.createElement('td');
    quantityCell.classList.add('text-center');
    const quantityInput = document.createElement('input');
    quantityInput.setAttribute('type', 'number');
    quantityInput.classList.add('form-control', 'border-0');
    quantityInput.setAttribute('form', 'form-pkb');
    quantityInput.setAttribute('value', 1);
    quantityInput.setAttribute('min', 1);
    quantityInput.setAttribute('id', `quantityInput_${rowIndex}`);
    quantityInput.addEventListener('input', calculateTotal); // Tính lại tổng khi thay đổi số lượng
    quantityCell.appendChild(quantityInput);
    newRow.appendChild(quantityCell);

    // Cột tồn kho
    const stockCell = document.createElement('td');
    stockCell.classList.add('text-center');
    const stockInput = document.createElement('input');
    stockInput.setAttribute('type', 'text');
    stockInput.classList.add('form-control', 'border-0');
    stockInput.setAttribute('readonly', 'true');
    stockInput.setAttribute('id', `stockInput_${rowIndex}`);
    stockCell.appendChild(stockInput);
    newRow.appendChild(stockCell);

    // Cột giá
    const priceCell = document.createElement('td');
    priceCell.classList.add('text-center');
    const priceInput = document.createElement('input');
    priceInput.setAttribute('type', 'text');
    priceInput.classList.add('form-control', 'border-0');
    priceInput.setAttribute('readonly', 'true');
    priceInput.setAttribute('id', `priceInput_${rowIndex}`);
    priceCell.appendChild(priceInput);
    newRow.appendChild(priceCell);

    // Cột tổng cộng
    const totalCell = document.createElement('td');
    totalCell.classList.add('text-center');
    const totalInput = document.createElement('input');
    totalInput.setAttribute('type', 'text');
    totalInput.classList.add('form-control', 'border-0');
    totalInput.setAttribute('readonly', 'true');
    totalInput.setAttribute('id', `totalInput_${rowIndex}`);
    totalCell.appendChild(totalInput);
    newRow.appendChild(totalCell);

    // Cột nút xóa
    const deleteCell = document.createElement('td');
    deleteCell.classList.add('text-center');
    const deleteButton = document.createElement('button');
    deleteButton.classList.add('btn', 'rounded-circle', 'btn-danger');
    deleteButton.innerHTML = '<i class="bi bi-x ">X</i>';
    deleteButton.addEventListener('click', function () {
        tableBodyy.removeChild(newRow); // Xóa dòng hiện tại
        updateRowIndexes(); // Cập nhật lại STT
        calculateTotal(); // Tính lại tổng sau khi xóa dòng
    });
    deleteCell.appendChild(deleteButton);
    newRow.appendChild(deleteCell);

    // Thêm dòng mới vào bảng
    tableBodyy.appendChild(newRow);

    drugInput.addEventListener('input', function () {
        // Lấy giá trị người dùng đã nhập
      const selectedDrug = drugInput.value.trim();

      // Lấy tất cả các options trong datalist
      const drugsOptions = document.querySelectorAll('#drugsList option');

      let drugFound = false;

     // Duyệt qua tất cả các option để tìm kiếm thuốc
         for (let option of drugsOptions) {
            if (option.value.trim().toLowerCase() === selectedDrug.toLowerCase()) {
            // Nếu tìm thấy thuốc, lấy thông tin
            const unit = option.getAttribute('data-unit');
            const stock = option.getAttribute('data-stock');
            const price = option.getAttribute('data-price');

            // Cập nhật thông tin vào các input tương ứng
            unitInput.value = unit;
            stockInput.value = stock;
            priceInput.value = price;

            // Tính tổng cộng
            totalInput.value = price * quantityInput.value;
            calculateTotal();
            // Đánh dấu là đã tìm thấy thuốc
            drugFound = true;
            break;  // Ngừng tìm kiếm khi đã tìm thấy thuốc
            }
         }

    if (!drugFound) {
        console.log("Không tìm thấy thuốc trong danh sách.");
    }
});

  // Lắng nghe sự kiện thay đổi số lượng để tính lại tổng cộng
    quantityInput.addEventListener('input', function () {
        const price = parseFloat(priceInput.value) || 0;
        const quantity = parseInt(quantityInput.value) || 1;
        totalInput.value = price * quantity; // Tính lại tổng cộng
        calculateTotal();



    });
    deleteButton.addEventListener('click', function () {
    const deletedDrug = drugInput.value.trim(); // Lấy giá trị tên thuốc trong dòng bị xóa

    // Xóa tên thuốc ra khỏi `Set`
    if (selectedDrugs.has(deletedDrug)) {
        selectedDrugs.delete(deletedDrug);
    }

    tableBody.removeChild(newRow); // Xóa dòng khỏi bảng
    updateRowIndexes(); // Cập nhật lại số thứ tự các dòng
    calculateTotal(); // Tính lại tổng giá trị
});
    // Hàm cập nhật lại STT
    function updateRowIndexes() {
        document.querySelectorAll('#tableBodyy tr').forEach((row, index) => {
            row.querySelector('td:first-child').textContent = index + 1;
        });
      }
    }

 function calculateTotal() {
    let grandTotal = 0;

    // Lấy tất cả các ô có id bắt đầu bằng 'totalInput_'
    const totalInputs = document.querySelectorAll('[id^="totalInput_"]');

    totalInputs.forEach(function(input) {
        const value = parseFloat(input.value) || 0; // Lấy giá trị trong ô totalInput và chuyển sang số (nếu không có giá trị thì mặc định là 0)
        grandTotal += value; // Cộng dồn vào tổng
    });

    // Cập nhật tổng cộng vào ô tổng (id="total")
      const formattedTotal = new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(grandTotal);

    // Cập nhật tổng cộng vào ô tổng (id="Total")
    document.getElementById("Total").value = formattedTotal; // Hiển thị định dạng tiền tệ VNĐ
}

 // Hàm cập nhật lại STT
    function updateRowIndexes() {
        document.querySelectorAll('#tableBodyy tr').forEach((row, index) => {
            row.querySelector('td:first-child').textContent = index + 1;
            calculateTotal();
        });
    }


function toggleButtons() {
    // Lấy các button từ DOM

    const btnSave = document.getElementById('btnSave'); // Nút Save
    const btnBack = document.getElementById('btnBack'); // Nút Back
    const btnSavePK = document.getElementById('btn-SavePK');
    const addRowBtn = document.getElementById('add-row-btn'); // Nút thêm dòng
    const deleteOptions = document.querySelectorAll('.btn.btn-danger'); // Các nút delete option (giả sử có class btn-danger)

    // Kiểm tra sự tồn tại của các phần tử trước khi thay đổi
    if (!btnSave || !btnBack || !addRowBtn) {
        console.error('Một số phần tử không tồn tại (btnSave, btnBack, add-row-btn)!');
        return;
    }

    // Khi btnSave bị ẩn, ẩn thêm delete options và addRowBtn
    if (btnSave.style.display === 'none') {
        btnSavePK.style.display='none';
        // Hiển thị btnSave và các nút liên quan
        btnSave.style.display = 'inline-block';
        btnBack.style.display = 'none';

        addRowBtn.style.display = 'inline-block'; // Hiển thị nút thêm dòng
        deleteOptions.forEach(function (button) {
            button.style.display = 'inline-block'; // Hiển thị các nút delete
        });
    } else {
        // Khi btnSave hiển thị, ẩn nó và các nút liên quan
        btnSave.style.display = 'none';
        btnSavePK.style.display='inline-block';
        btnBack.style.display = 'inline-block';
        addRowBtn.style.display = 'none'; // Ẩn nút thêm dòng
        deleteOptions.forEach(function (button) {
            button.style.display = 'none'; // Ẩn các nút delete
        });
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const btnSave = document.getElementById('btnSave');
    const btnBack = document.getElementById('btnBack');

    if (btnSave) {
        btnSave.addEventListener('click', function (event) {
            event.preventDefault(); // Ngăn form submit
            toggleButtons(); // Thực hiện hàm toggleButtons ngay
        });
    }

    if (btnBack) {
        btnBack.addEventListener('click', function (event) {
            event.preventDefault(); // Ngăn form submit
            toggleButtons(); // Thực hiện hàm toggleButtons ngay
        });
    }
});
// Khởi chạy hàm khi DOM đã hoàn tất tải

setTimeout(function () {
        const flashMessages = document.querySelectorAll('.alert');
        flashMessages.forEach(function (message) {
            message.classList.add('fade-out'); // Thêm class để ẩn

            setTimeout(() => message.remove(), 500); // Xóa khỏi DOM sau khi ẩn
        });
    }, 3000); // 3000ms = 3 giây



function updateLoaiBenh() {
    // Lấy giá trị từ trường input 'Res' (chuẩn đoán)
    const benhField = document.getElementById('Res');
    const loaiBenhIdField = document.getElementById('loaibenh_id');

    // Lấy danh sách các options từ datalist
    const benhDatalist = document.getElementById('BenhList');
    const selectedValue = benhField.value;

    // Tìm option khớp với giá trị 'Res'
    const matchedOption = Array.from(benhDatalist.options).find(option => option.value === selectedValue);

    // Nếu tìm thấy, đặt giá trị cho trường 'loaibenh_id'
    if (matchedOption) {
        loaiBenhIdField.value = matchedOption.id; // Truy cập 'id' của option
    } else {
        // Nếu không tìm thấy, đặt giá trị rỗng
        loaiBenhIdField.value = '';
    }
}



function submitDrugData() {
    const tableBodyy = document.getElementById('tableBodyy'); // Lấy tbody của bảng
    const rows = tableBodyy.querySelectorAll('tr'); // Lấy tất cả các hàng (tr)

    const drugData = []; // Mảng chứa thông tin các dòng

    rows.forEach((row, index) => {
        const drugInput = row.querySelector(`#drugInput_${index + 1}`); // Lấy input của cột thuốc
        const quantityInput = row.querySelector(`#quantityInput_${index + 1}`); // Lấy input của cột số lượng

        if (drugInput && quantityInput) {
            drugData.push({
                drugName: drugInput.value, // Lấy tên thuốc từ input
                quantity: parseInt(quantityInput.value) || 0 // Lấy số lượng (nếu không có thì mặc định là 0)
            });
        }
    });

    console.log("Dữ liệu gửi đi:", drugData);

    // Gửi dữ liệu qua Fetch API đến Flask
    fetch('/api/process-data', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(drugData) // Gửi dữ liệu dạng JSON
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response from server:", data);
        alert(data.message); // Hiển thị thông báo từ server

        // Reload lại trang
        location.reload();
    })
    .catch(error => {

    });
}