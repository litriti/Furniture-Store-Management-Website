function confirmOrder(receiptId) {
    if (confirm("Bạn có chắc chắn muốn xác nhận đơn hàng này?")) {
        // Gửi yêu cầu AJAX tới server để xác nhận đơn hàng
        fetch(`/confirm_order/${receiptId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token() }}'  // Đảm bảo bảo mật CSRF
            },
            body: JSON.stringify({ active: 0 })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Đơn hàng đã được xác nhận.");
                // Cập nhật giao diện hoặc tải lại trang để hiển thị thay đổi
                location.reload();
            } else {
                alert("Đã xảy ra lỗi. Vui lòng thử lại.");
            }
        })
        .catch(error => {
            console.error("Lỗi:", error);
        });
    }
}

function openModal(Id) {
    // Mở modal
    $('#confirmOrderModal').modal('show');
    // Gán orderId cho nút Gửi đánh giá
    document.querySelector('.btn-primary').setAttribute('receipt-id', id);
}

function setRating(rating) {
    // Cập nhật đánh giá sao
    document.getElementById('starRating').value = rating;
    const stars = document.querySelectorAll('.star');
    stars.forEach((star, index) => {
        star.style.color = index < rating ? 'gold' : 'gray'; // Đổi màu ngôi sao
    });
}

function submitReview(orderId) {
    const rating = document.getElementById('starRating').value;
    const comment = document.getElementById('comment').value;

    // Gửi dữ liệu đánh giá đến server (có thể sử dụng AJAX)
    console.log(`Order ID: ${orderId}, Rating: ${rating}, Comment: ${comment}`);

    // Đóng modal sau khi gửi
    $('#confirmOrderModal').modal('hide');

    // Xóa thông tin cũ trong modal
    document.getElementById('starRating').value = 0;
    document.getElementById('comment').value = '';
    setRating(0); // Reset ngôi sao
}