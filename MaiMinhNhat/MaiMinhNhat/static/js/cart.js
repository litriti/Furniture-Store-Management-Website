function addToCart(id, name, price) {
    fetch("/api/carts", {
       method: "post",
       body: JSON.stringify({
            "id": id,
            "name": name,
            "price": price
       }),
       headers: {
            "Content-Type": "application/json"
       }
    }).then(res => res.json()).then(data => {
        let d = document.getElementsByClassName("cart-counter");
        for (let e of d)
            e.innerText = data.total_quantity;

        let d3 = document.getElementsByClassName("cart-product");
        for (let e of d3)
            e.innerText = data.total_product;

          // Tạo modal để hiển thị thông báo
        let modal = document.createElement("div");
        modal.className = "cart-modal";

        let modalContent = document.createElement("div");
        modalContent.className = "cart-modal-content";
        modalContent.innerText = "Đã thêm vào giỏ hàng thành công";

        modal.appendChild(modalContent);
        document.body.appendChild(modal);

        // Tự động ẩn thông báo sau 1 giây
        setTimeout(() => {
            modal.remove();
        }, 1000);
    });
}



function updateCart(productId, obj) {
    fetch(`/api/cart/${productId}`, {
        method: "put",
        body: JSON.stringify({
            "quantity": parseInt(obj.value)
        }),
        headers: {
            "Content-Type": "application/json"
       }
    }).then(res => res.json()).then(data => {
        let d = document.getElementsByClassName("cart-counter");
        for (let e of d)
            e.innerText = data.total_quantity;

        let d2 = document.getElementsByClassName("cart-amount");
        for (let e of d2)
            e.innerText = data.total_amount.toLocaleString("en");

        let d3 = document.getElementsByClassName("cart-product");
        for (let e of d3)
            e.innerText = data.total_product;
    });
}


function deleteCart(productId) {
    if (confirm("Bạn chắc chắn xóa sản phẩm khỏi giỏ?") === true) {
        fetch(`/api/cart/${productId}`, {
            method: "delete"
        }).then(res => res.json()).then(data => {
            let d = document.getElementsByClassName("cart-counter");
            for (let e of d)
                e.innerText = data.total_quantity;

            let d2 = document.getElementsByClassName("cart-amount");
            for (let e of d2)
                e.innerText = data.total_amount.toLocaleString("en");

            let d3 = document.getElementsByClassName("cart-product");
            for (let e of d3)
                e.innerText = data.total_product;

            let e = document.getElementById(`product${productId}`);
            e.style.display = "none";
            location.reload(); // Tải lại trang để cập nhật
        });
    }
}



 function pay() {
        // Kiểm tra tính hợp lệ của form
        const name = document.getElementById('name').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const address = document.getElementById('address').value.trim();
        //
        const cash_option = document.querySelector('input[name="payment_method"]:checked').value;


        if (!name || !phone || !address) {
            Swal.fire({
                icon: 'warning',
                title: 'Thông báo',
                text: 'Vui lòng điền đầy đủ thông tin!',
                confirmButtonText: 'OK'
            });
            return; // Ngăn không cho thực hiện tiếp
        }

        // Thay thế confirm bằng SweetAlert
        Swal.fire({
            title: 'Xác nhận thanh toán?',
            text: "Bạn chắc chắn muốn thực hiện thanh toán này?",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Có',
            cancelButtonText: 'Không'
        }).then((result) => {
            if (result.isConfirmed) {
                // Gửi yêu cầu đến server
                fetch("/api/pay", {
                    method: 'POST',
                    body: JSON.stringify({
                        name: name,
                        phone: phone,
                        address: address,
                        cash_option: cash_option
                    }),
                    headers: {
                        "Content-Type": "application/json"
                    }
                })
                .then(res => {
                    if (!res.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return res.json();
                })
                .then(data => {
                    if (data.status === 200) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Thành công!',
                            text: 'Thanh toán thành công!',
                            confirmButtonText: 'OK'
                        }).then(() => {
                            location.reload(); // Tải lại trang để cập nhật
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Có lỗi xảy ra!',
                            text: data.message || 'Có lỗi xảy ra khi thanh toán.',
                            confirmButtonText: 'OK'
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Có lỗi xảy ra!',
                        text: 'Có lỗi xảy ra khi thanh toán.',
                        confirmButtonText: 'OK'
                    });
                });
            }
        });
    }