//function validateForm() {
//    // Lấy giá trị từ các trường trong form
//    const name = document.getElementById('name').value.trim();
//    const phone = document.getElementById('phone').value.trim();
//    const address = document.getElementById('address').value.trim();
//
//    // Kiểm tra nếu các trường rỗng hoặc không hợp lệ
//    if (!name || !phone || !address || phone.length < 10 || phone.length > 11 || address.length < 10) {
//        alert("Vui lòng điền đầy đủ và chính xác thông tin.");
//        return false;  // Ngăn không cho form được submit
//    }
//
//    return true;  // Cho phép form được submit
//}
//
//// Lắng nghe sự kiện submit của form
//document.getElementById('checkoutForm').addEventListener('submit', function(event) {
//    if (!validateForm()) {
//        event.preventDefault();  // Ngăn không cho form được submit
//    }
//});
