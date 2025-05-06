import io
import math
from datetime import datetime
from idlelib.query import Query
from xmlrpc.client import DateTime

import requests
from click import DateTime
from flask import render_template, request, redirect, session, jsonify, flash, url_for
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import current_time

import dao
import utils
from MaiMinhNhat import app, login, db
from flask_login import login_user, logout_user, login_required, current_user
import cloudinary.uploader

from MaiMinhNhat.dao import load_receipt_details, get_user_by_id
from MaiMinhNhat.models import UserRole, User, Receipt, ReceiptDetails, ORDER_STATUS_LABELS, Product, OrderStatus
from decorators import loggedin
import qrcode
import qrcode

import io
from io import BytesIO
from flask import send_file, make_response


def create_vietqr(account_number, bank_code, amount, description):
    base_url = "https://api.vietqr.net/generate"

    # Payload gửi đến API để tạo mã QR
    payload = {
        "accountNumber": account_number,
        "bankCode": bank_code,
        "amount": amount,
        "description": description
    }

    response = requests.post(base_url, json=payload)

    if response.status_code == 200:
        # Trả về URL của mã QR nếu thành công
        qr_data = response.json()
        return qr_data['qrData']
    else:
        print(f"Lỗi khi tạo mã VietQR: {response.status_code}")
        return None


@app.route('/generate_qr')
def generate_qr_api():
    total_amount = request.args.get('total_amount', default=0, type=int)
    account_number = "7642807"  # Thay bằng số tài khoản của bạn
    bank_code = "ACB"  # Thay bằng mã ngân hàng của bạn
    description = "Thanh toán đơn hàng"  # Mô tả thanh toán

    # Đảm bảo số tiền là số dương
    if total_amount <= 0:
        return "Số tiền không hợp lệ", 400

    # # Tạo dữ liệu mã QR theo định dạng VietQR
    # qr_data = f"VietQR|{account_number}|{bank_code}|{total_amount}|{description}"

    # Gọi API tạo mã QR
    # qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?data={qr_data}&size=200x200"
    qr_api_url = f"https://api.vietqr.io/image/970416-7642807-kHk3Ni4.jpg?accountName=MAI%20MINH%20NHAT&amount={total_amount}&addInfo=thanh%20toan%20don%20hang"

    # Lấy ảnh mã QR từ API
    response = requests.get(qr_api_url)

    # Nếu API trả về mã 200, trả về ảnh QR
    if response.status_code == 200:
        return send_file(io.BytesIO(response.content), mimetype='image/png')

    return "Không thể tạo mã QR", 500


# @app.route('/generate_qr')
# def generate_qr():
#     current_date = datetime.now().strftime('%d-%m-%Y')
#     total_amount = request.args.get('total_amount', default=0, type=int)
#     account_number = "7642807"  # Thay bằng số tài khoản của bạn
#     bank_code = "ACB"  # Thay bằng mã ngân hàng của bạn
#     description = "Thanh toán đơn hàng"  # Mô tả thanh toán
#
#     # Thông tin thanh toán
#     payment_info = f'Thanh toán đơn hàng ngày {current_date} - Số tiền: {total_amount} VND'
#
#     # Tạo dữ liệu mã QR theo định dạng VietQR
#     qr_data = f"VietQR|{account_number}|{bank_code}|{total_amount}|{description}"
#
#     # Tạo mã QR từ dữ liệu
#     qr_img = qrcode.make(qr_data)
#
#
#
#     # Tạo mã QR
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(payment_info)
#     qr.make(fit=True)
#
#     img = qr.make_image(fill='black', back_color='white')
#
#     # Lưu mã QR vào bộ nhớ
#     img_io = io.BytesIO()
#     qr_img.save(img_io, 'PNG')
#     img_io.seek(0)
#
#     # Trả về mã QR dưới dạng file ảnh
#     return send_file(img_io, mimetype='image/png')



# @app.route('/')
# def index():
#     q = request.args.get('q')
#     cate_id = request.args.get('category_id')
#     page = request.args.get('page')
#
#     products = dao.load_products(q=q, cate_id=cate_id, page=page)
#     return render_template('index.html', products=products,
#                            pages=math.ceil(dao.count_product() / app.config['PAGE_SIZE']))


@app.route('/')
def index():
    q = request.args.get('q')
    cate_id = request.args.get('category_id')
    page = request.args.get('page')
    sort_order = request.args.get('sort_order')  # Thêm tham số này
    total_products = dao.count_product()
    pages = math.ceil(total_products / 8)
    products = dao.load_products(q=q, cate_id=cate_id, page=page,sort_order=sort_order)

    return render_template('index.html', products=products,
                           pages=pages)


@app.route('/products/<int:id>')
def details(id):
    product = dao.get_product_by_id(product_id=id)
    comments = dao.get_comments(product_id=id)

    # Lấy các tag của sản phẩm hiện tại
    tags = dao.get_product_tags(product_id=id)

    # Tìm các sản phẩm gợi ý từ tag nếu có
    suggested_products = []
    if tags:
        for tag in tags:
            suggested_products.extend(dao.suggest_products(tag_name=tag.name, category_id=product.category_id))
    else:
        # Nếu không có tag, gợi ý các sản phẩm cùng loại
        suggested_products = Product.query.filter(Product.category_id == product.category_id, Product.id != id).all()

        # Loại bỏ sản phẩm hiện tại và duy trì tối đa 4 sản phẩm
    suggested_products = list({p.id: p for p in suggested_products if p.id != id}.values())[:4]
    return render_template('product-details.html', product=product, comments=comments, suggested_products=suggested_products)


# @app.route('/products/<int:id>')
# def details(id):
#     product = dao.get_product_by_id(product_id=id)
#     comments = dao.get_comments(product_id=id)
#     return render_template('product-details.html', product=product, comments=comments)
@app.route('/address/')
def location():

    return render_template('address.html')


@app.route('/order-tracking/')
@login_required  # Đảm bảo người dùng đã đăng nhập
def order_tracking():

    receipt = dao.load_receipt()
    receipt_details = dao.load_receipt_details(receipt_id=Receipt.id)
    products = dao.tracking_product()
    # Lấy các đơn hàng của người dùng hiện tại
    orders = Receipt.query.filter_by(user_id=current_user.id).all()

    # Tính tổng giá cho từng đơn hàng
    temp = {order.id: order.total_price for order in orders}
    return render_template('order-tracking.html', receipt=receipt, receipt_details=receipt_details, products=products, temp=temp, status_labels = ORDER_STATUS_LABELS,orders=orders)


@app.route('/confirm_order/<int:receipt_id>', methods=['POST'])
def confirm_order(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    if receipt.active:  # Chỉ xác nhận nếu đơn hàng vẫn còn active
        receipt.active = False  # Đặt cột active thành False (0)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})


@app.route('/login', methods=['get', 'post'])
@loggedin
def login_my_user():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)

            next = request.args.get('next')
            return redirect(next if next else '/')
        else:
            err_msg = 'Username hoặc password không đúng!'

    return render_template('login.html', err_msg=err_msg)


@app.route('/logout', methods=['get'])
def logout_my_user():
    logout_user()
    return redirect('/login')


@app.route("/admin-login", methods=['post'])
def process_admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    u = dao.auth_user(username=username, password=password)
    if u:
        login_user(user=u)

    return redirect('/admin')


@app.route('/register', methods=['get', 'post'])
@loggedin
def register_user():
    err_msg = None
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        username = request.form.get('username')
        have_username = dao.get_user_by_username('username')

        if password.__eq__(confirm):
            avatar_path = None
            avatar = request.files.get('avatar')
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                avatar_path = res['secure_url']
            elif avatar_path is None:
                avatar_path = 'https://res.cloudinary.com/dzo5vlw1o/image/upload/v1723963545/tg20vzmknpjwpvwek0be.png'

            dao.add_user(name=request.form.get('name'),
                         username=request.form.get('username'),
                         password=password,
                         avatar=avatar_path)

            return redirect('/login')

        else:
            err_msg = 'Mật khẩu không khớp!'


    return render_template('register.html', err_msg=err_msg)


@app.route('/api/carts', methods=['post'])
def add_to_cart():
    """
    {
        "cart": {
            "1": {
                "id": "",
                "name": "...",
                "price": "...",
                "quantity": 2
            }, "2": {
                "name": "...",
                "price": "...",
                "quantity": 1
            }
        }
    }
    :return:
    """
    data = request.json
    id = str(data['id'])

    key = app.config['CART_KEY']  # 'cart'
    cart = session[key] if key in session else {}
    if id in cart:
        cart[id]['quantity'] += 1
    else:
        name = data['name']
        price = data['price']
        cart[id] = {
            "id": id,
            "name": name,
            "price": price,
            "quantity": 1
        }

    session[key] = cart

    return jsonify(utils.count_cart(cart=cart))


@app.route('/cart')
def cart():
    current_date = datetime.now().strftime('%d-%m-%Y')
    return render_template('cart.html',current_date =current_date)


# @app.route('/pay')
# def page_pay():
#     return render_template('page-pay.html')


@app.route('/api/cart/<product_id>', methods=['put'])
def update_cart(product_id):
    cart = session.get('cart')
    if cart and product_id in cart:
        cart[product_id]['quantity'] = request.json['quantity']
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/cart/<product_id>', methods=['delete'])
def delete_cart(product_id):
    cart = session.get('cart')
    # Xóa sản phẩm nếu product_id có trong giỏ hàng
    if product_id in cart:
        del cart[product_id]

    # Kiểm tra nếu giỏ hàng trống sau khi xóa
    if not cart:
        session.pop('cart', None)  # Xóa toàn bộ giỏ hàng nếu không còn sản phẩm nào
    else:
        session['cart'] = cart  # Cập nhật lại giỏ hàng sau khi xóa sản phẩm

    return jsonify(utils.count_cart(cart))


# @app.route("/api/pay", methods=['post'])
# @login_required
# def pay():
#     cart = session.get('cart')
#
#     # Lưu thông tin nhận hàng vào database
#     try:
#         dao.add_receipt(cart)
#     except Exception as ex:
#         print(ex)
#         return jsonify({'status': 500})
#     else:
#         del session['cart']
#         flash("Thông tin thanh toán đã được gửi thành công!")
#         return jsonify({'status': 200})


@app.route("/api/pay", methods=['post'])
@login_required
def pay():
    cart = session.get('cart')
    data = request.json  # Lấy dữ liệu JSON gửi từ phía frontend

    # Lấy thông tin bổ sung
    name = data.get('name')
    phone = data.get('phone')
    address = data.get('address')
    cash_option = data.get('cash_option')

    # Lưu thông tin nhận hàng vào cơ sở dữ liệu
    try:
        dao.add_receipt(cart, name=name, phone=phone, address=address, cash_option=cash_option)  # Thay đổi phương thức dao của bạn cho phù hợp
    except Exception as ex:
        print(ex)
        return jsonify({'status': 500})
    else:
        del session['cart']
        flash("Thông tin thanh toán đã được gửi thành công!")
        return jsonify({'status': 200})


@app.route('/api/receipts/<int:id>/confirm', methods=['POST'])
@login_required
def confirm_receipt(id):
    receipt = Receipt.query.get(id)

    if receipt.order_status != OrderStatus.DELIVERY:
        return jsonify({'status': 400, 'message': 'Trạng thái đơn hàng không hợp lệ!'}), 400

    receipt.mark_as_completed()
    db.session.commit()

    return jsonify({'status': 200, 'message': 'Đơn hàng đã được xác nhận nhận hàng và chuyển sang Hoàn thành.'})


@app.route('/api/products/<int:id>/comments', methods=['post'])
@login_required
def add_comment(id):
    # Lấy thông tin người dùng hiện tại
    user_id = current_user.id

    # Kiểm tra xem người dùng đã mua sản phẩm này chưa
    has_purchased = dao.check_if_user_purchased(user_id=user_id, product_id=id)


    # Kiểm tra xem đã có bình luận cho sản phẩm này trong đơn hàng chưa
    has_commented_count = dao.count_receipt_have_product_id(user_id=user_id, product_id=id)

    if not has_purchased:
        return jsonify({'status': 403, 'error': 'Bạn chưa mua sản phẩm này!!!'}), 403


    if has_commented_count<= dao.check_if_user_commented(user_id=user_id, product_id=id):
        return jsonify({'status': 403, 'error': 'Bạn chỉ được bình luận một lần cho sản phẩm này!'}), 403

    data = request.json
    c = dao.add_comment(content=data.get('content'), product_id=id)

    return jsonify({'id': c.id, 'content': c.content, 'user': {
        'username': c.user.name,
        'avatar': c.user.avatar
    }})


@app.context_processor
def common_attributes():
    return {
        'categories': dao.load_categories(),
        'cart_stats': utils.count_cart(session.get('cart'))
    }


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == '__main__':
    with app.app_context():
        from MaiMinhNhat import admin

        app.run(debug=True)
