function toggleDetails(id) {
    var details = document.getElementById('receipt_details_' + id);
    if (details.classList.contains('d-none')) {
            details.classList.remove('d-none');
        }
    else {
            details.classList.add('d-none');
        }
}

