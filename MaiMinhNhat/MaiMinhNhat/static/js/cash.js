function setupPaymentToggle(paymentCodId, paymentMomoId, payButtonCodId, payButtonMomoId) {
    const paymentCOD = document.getElementById(paymentCodId);
    const paymentMoMo = document.getElementById(paymentMomoId);
    const payButtonCOD = document.getElementById(payButtonCodId);
    const payButtonMoMo = document.getElementById(payButtonMomoId);

    // Lắng nghe sự thay đổi khi người dùng chọn phương thức thanh toán
    paymentCOD.addEventListener('change', function() {
        if (this.checked) {
            payButtonCOD.style.display = 'block';  // Hiển thị nút thanh toán COD
            payButtonMoMo.style.display = 'none';  // Ẩn nút thanh toán MoMo
        }
    });

    paymentMoMo.addEventListener('change', function() {
        if (this.checked) {
            payButtonMoMo.style.display = 'block';  // Hiển thị nút thanh toán MoMo
            payButtonCOD.style.display = 'none';  // Ẩn nút thanh toán COD
        }
    });
}
