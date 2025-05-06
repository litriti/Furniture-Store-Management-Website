function confirmReceipt(receiptId) {
    fetch(`/api/receipts/${receiptId}/confirm`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 200) {
            alert(data.message);
            window.location.reload();
        } else {
            alert('Có lỗi xảy ra: ' + data.message);
        }
    });
}
