from functools import wraps

import requests
from flask import request, redirect, url_for
from flask_login import current_user
import qrcode


def loggedin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index', next=request.url))

        return f(*args, **kwargs)

    return decorated_function


# def create_vietqr(account_number, bank_code, amount, description):
#     base_url = "https://api.vietqr.net/generate"
#
#     # Payload gửi đến API để tạo mã QR
#     payload = {
#         "accountNumber": account_number,
#         "bankCode": bank_code,
#         "amount": amount,
#         "description": description
#     }
#
#     response = requests.post(base_url, json=payload)
#
#     if response.status_code == 200:
#         # Trả về URL của mã QR nếu thành công
#         qr_data = response.json()
#         return qr_data['qrData']
#     else:
#         print(f"Lỗi khi tạo mã VietQR: {response.status_code}")
#         return None
#
#
# # Ví dụ sử dụng hàm để tạo mã QR
# account_number = "0123456789"  # Số tài khoản nhận tiền
# bank_code = "BIDV"  # Mã ngân hàng
# amount = 1000000  # Số tiền (1.000.000 VND)
# description = "Thanh toán đơn hàng #12345"
#
# qr_data = create_vietqr(account_number, bank_code, amount, description)
#
# # Tạo và hiển thị mã QR nếu thành công
# if qr_data:
#     img = qrcode.make(qr_data)
#     img.show()  # Hoặc lưu lại: img.save("vietqr.png")