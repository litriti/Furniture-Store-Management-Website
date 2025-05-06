function resetForm() {
    document.getElementById('starRating').value = 0;
    document.getElementById('comment').value = '';
    setRating(0); // Reset ngôi sao
    $('#confirmOrderModal').modal('hide'); // Đóng modal
}