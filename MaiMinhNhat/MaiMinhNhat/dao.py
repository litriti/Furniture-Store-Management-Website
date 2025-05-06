import requests
from sqlalchemy.dialects import mysql

from MaiMinhNhat.models import Category, Product, User, Receipt, ReceiptDetails, Comment, Tag, OrderStatus
from flask_login import current_user
from MaiMinhNhat import app, db
from sqlalchemy import func
import hashlib
from datetime import datetime

import MySQLdb


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


def load_categories():
    return Category.query.all()


def count_product():
    return Product.query.count()


def count_product_by_cate():
    return

# def load_products(q=None, cate_id=None, page=None, kw=None):
#     query = Product.query
#
#     if q:
#         query = query.filter(Product.name.contains(q))
#
#     if cate_id:
#         query = query.filter(Product.category_id.__eq__(cate_id))
#
#     if page:
#         page_size = app.config['PAGE_SIZE']
#         start = (int(page) - 1) * page_size
#         query = query.slice(start, start + page_size)
#
#     return query.all()


def get_product_tags(product_id):
    product = Product.query.get(product_id)
    return product.tags  # Giả định rằng product.tags là một danh sách các đối tượng Tag


def suggest_products(tag_name, category_id):
    return Product.query.filter(Product.category_id == category_id,
                                 Product.tags.any(Tag.name == tag_name)).all()


# def load_products(q=None, cate_id=None, page=None, sort_order=None):
#     query = Product.query
#
#     if q:
#         query = query.filter(Product.name.ilike(f'%{q}%'))
#
#     # phần sắp xếp theoo giá
#     if sort_order == 'price_asc':
#         query = query.order_by(Product.price.asc())
#
#     elif sort_order == 'price_desc':
#         query = query.order_by(Product.price.desc())
#
#     else:
#         query = query.order_by(Product.id.asc())
#
#     if cate_id:
#         query = query.filter(Product.category_id.__eq__(cate_id))
#
#     if page:
#         page_size = app.config['PAGE_SIZE']
#         start = (int(page) - 1) * page_size
#         query = query.slice(start, start + page_size)
#
#     products = query.all()
#     return query.all()



def tracking_product(q=None):
    query = Product.query

    # Tìm kiếm sản phẩm theo tên
    if q:
        query = query.filter(Product.name.ilike(f'%{q}%'))

    products = query.all()
    return products  # Trả về danh sách sản phẩm


def load_products(q=None, cate_id=None, page=1, sort_order=None):
    query = Product.query

    # Tìm kiếm sản phẩm theo tên
    if q:
        query = query.filter(Product.name.ilike(f'%{q}%'))

    # Sắp xếp theo giá hoặc tên
    if sort_order == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_order == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_order == 'name_asc':  # Sắp xếp theo tên A-Z
        query = query.order_by(Product.name.asc())
    elif sort_order == 'name_desc':  # Sắp xếp theo tên Z-A
        query = query.order_by(Product.name.desc())
    else:
        query = query.order_by(Product.id.asc())

    # Lọc theo danh mục sản phẩm
    if cate_id:
        query = query.filter(Product.category_id == cate_id)

    # Phân trang

    page_size = app.config['PAGE_SIZE']
    page = int(page) if page else 1  # Mặc định trang 1 nếu không có trang được chỉ định
    start = (page - 1) * page_size
    query = query.slice(start, start + page_size)

    products = query.all()
    return products  # Trả về danh sách sản phẩm



def load_receipt():
    if current_user.is_authenticated:
        user_id = current_user.id  # Lấy user_id của người dùng đang đăng nhập
        receipts = Receipt.query.filter_by(user_id=user_id).all()
        return receipts
    else:
        return None


def load_receipt_details(receipt_id):
    details = ReceiptDetails.query.filter_by(receipt_id=receipt_id).all()
    return details


def get_product_by_id(product_id):
    return Product.query.get(product_id)


def get_user_by_id(id):
    return User.query.get(id)


def get_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_receipt_by_id(receipt_id: int) -> Receipt:
    return Receipt.query.get_or_404(receipt_id)


def get_user_receipts_with_details(username):
    # Truy vấn để lấy thông tin Receipt, ReceiptDetails và Product
    receipts = (Receipt.query.filter(Receipt.id, Receipt.created_date, ReceiptDetails.price, ReceiptDetails.quantity,
                                     Product.name)
                .join(ReceiptDetails, Receipt.id == ReceiptDetails.receipt_id)
                .join(Product, ReceiptDetails.product_id == Product.id)
                .filter(Receipt.user_id == User.id)
                .all()
                )

    return receipts


def get_receipt_details_by_user(user_id):
    return ReceiptDetails.query.get(user_id)


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username, password=password, avatar=avatar)
    db.session.add(u)
    db.session.commit()



def add_receipt(cart,name, phone, address, cash_option):
    if cart:
        r = Receipt(user=current_user,name=name, phone=phone, address=address, cash_option=cash_option)
        db.session.add(r)

        for c in cart.values():
            d = ReceiptDetails(quantity=c['quantity'], price=c['price'],
                               receipt=r, product_id=c['id'])
            db.session.add(d)

        db.session.commit()



def count_products_by_cate():
    return db.session.query(Category.id, Category.name,
                            func.count(Product.id)).join(Product, Product.category_id.__eq__(Category.id), isouter=True) \
        .group_by(Category.id).all()


def stats_revenue_by_product(kw=None):
    query = db.session.query(Product.id, Product.name,
                             func.sum(ReceiptDetails.quantity * ReceiptDetails.price)) \
        .join(ReceiptDetails, ReceiptDetails.product_id.__eq__(Product.id), isouter=True)

    if kw:
        query = query.filter(Product.name.contains(kw))

    return query.group_by(Product.id).all()


def stats_revenue_by_period(year=datetime.now().year, period='month'):
    query = db.session.query(func.extract(period, Receipt.created_date),
                             func.sum(ReceiptDetails.quantity * ReceiptDetails.price)) \
        .join(ReceiptDetails, ReceiptDetails.receipt_id.__eq__(Receipt.id)) \
        .filter(func.extract('year', Receipt.created_date).__eq__(year))

    return query.group_by(func.extract(period, Receipt.created_date)) \
        .order_by(func.extract(period, Receipt.created_date)).all()


def check_if_user_commented(user_id, product_id):

    return Comment.query.filter_by(user_id=user_id, product_id=product_id).count()


def count_receipt_have_product_id(user_id, product_id):
    # Count the number of distinct receipts that contain the product
    return db.session.query(ReceiptDetails).join(Receipt).filter(
        Receipt.user_id == user_id,
        ReceiptDetails.product_id == product_id,
        Receipt.order_status == OrderStatus.COMPLETED
    ).distinct(ReceiptDetails.receipt_id).count()


# def get_user_purchases_count(user_id, product_id):
#     # Lấy số lần người dùng đã mua sản phẩm này
#     return db.session.query(ReceiptDetails).join(Receipt).filter(
#         Receipt.user_id == user_id,
#         Receipt.order_status == 'Đã giao hàng'  # Kiểm tra chỉ những đơn hàng đã giao
#     ).count()


# def get_user_comments_count(user_id, product_id):
#     # Lấy số lần người dùng đã bình luận về sản phẩm này
#     return Comment.query.filter_by(user_id=user_id, product_id=product_id).count()


def check_if_user_purchased(user_id, product_id):
    return db.session.query(ReceiptDetails).join(Receipt).filter(
        Receipt.user_id == user_id,
        ReceiptDetails.product_id == product_id
    ).first() is not None


def get_comments(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).order_by(-Comment.id)


def add_comment(content, product_id):
    c = Comment(content=content, product_id=product_id, user=current_user)
    db.session.add(c)
    db.session.commit()

    return c


if __name__ == '__main__':
    with app.app_context():
        print(count_products_by_cate())
