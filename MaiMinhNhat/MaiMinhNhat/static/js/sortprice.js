 // Hàm định dạng số với dấu phẩy
    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    // Cập nhật giá trị hiển thị của thanh kéo
    function updatePriceDisplay(value) {
        document.getElementById('price_range_value').innerText = formatNumber(value);
    }

    // Cập nhật hiển thị giá trị khi trang load
    window.onload = function() {
        const priceRangeInput = document.getElementById('price_range');
        updatePriceDisplay(priceRangeInput.value);
    };