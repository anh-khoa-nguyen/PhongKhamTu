
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

