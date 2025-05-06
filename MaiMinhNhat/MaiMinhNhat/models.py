import hashlib
from idlelib.query import Query
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum, Boolean, DateTime, Text
from sqlalchemy.orm import relationship, backref, Relationship
from MaiMinhNhat import db, app
from flask_login import UserMixin
from enum import Enum as RoleEnum
from datetime import datetime, timedelta


class UserRole(RoleEnum):
    USER = 1
    ADMIN = 2
    MANAGER = 3


class OrderStatus(RoleEnum):
    CONFIRMED = 1
    SHIPPING = 2
    DELIVERY = 3
    COMPLETED = 4


ORDER_STATUS_LABELS = {
    OrderStatus.CONFIRMED: "Đã xác nhận",
    OrderStatus.SHIPPING: "Đang giao hàng",
    OrderStatus.DELIVERY: "Đã giao hàng",
    OrderStatus.COMPLETED: "Hoàn thành"
}


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, autoincrement=True, primary_key=True)
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now())


class User(BaseModel, UserMixin):
    name = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    receipts = relationship('Receipt', backref='user', lazy=True)
    comments = relationship('Comment', backref='user', lazy=True)

    def __str__(self):
        return self.name


class Category(BaseModel):
    __tablename__ = 'category'

    name = Column(String(50), unique=True, nullable=False)
    products = relationship('Product', backref='category', lazy=True)

    def __str__(self):
        return self.name


prod_tag = db.Table('prod_tag',
                    Column('product_id', Integer, ForeignKey('product.id'), primary_key=True),
                    Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True))


class Product(BaseModel):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    price = Column(Float, default=0)
    image = Column(String(100))
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    receipt_details = relationship('ReceiptDetails', backref='product', lazy=True)
    comments = relationship('Comment', backref='product', lazy=True)
    tags = relationship('Tag', secondary='prod_tag', lazy='subquery',
                        backref=backref('products', lazy=True))

    def __str__(self):
        return self.name


class Tag(BaseModel):
    name = Column(String(50), nullable=False, unique=True)

    def __str__(self):
        return self.name


class Receipt(BaseModel):
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=False)
    address = Column(String(100), nullable=False)

    cash_option = Column(String(100), nullable=False)

    order_status = Column(Enum(OrderStatus), default=OrderStatus.CONFIRMED)
    details = relationship('ReceiptDetails', backref='receipt', lazy=True)

    completed_at = Column(DateTime)  # Thời gian khi đơn hàng hoàn thành

    @property
    def total_price(self):
        return sum(detail.quantity * detail.price for detail in self.details)

    @property
    def order_status_label(self):
        return ORDER_STATUS_LABELS.get(self.order_status, "Không xác định")

    def mark_as_completed(self):
        self.order_status = OrderStatus.COMPLETED
        self.completed_at = datetime.now()


class ReceiptDetails(BaseModel):
    quantity = Column(Integer, default=0)
    price = Column(Float, default=0)
    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)

    # Tính thời gian để cho phép bình luận (30 phút sau khi nhận hàng)
    def is_comment_allowed(self):
        receipt = Receipt.query.get(self.receipt_id)
        if receipt.order_status == OrderStatus.COMPLETED:
            time_since_completed = datetime.now() - receipt.completed_at
            return time_since_completed <= timedelta(minutes=1)
        return False


class Comment(BaseModel):
    content = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        import json

        with open('data/categories.json', encoding='utf-8') as f:
            categories = json.load(f)
            for c in categories:
                cate = Category(**c)
                db.session.add(cate)

        db.session.commit()

        import json

        with open('data/products.json', encoding='utf-8') as f:
            products = json.load(f)
            for p in products:
                prod = Product(**p)
                db.session.add(prod)

        db.session.commit()

        #
        import hashlib

        u = User(name='admin', username='admin',
                 avatar='https://res.cloudinary.com/dzo5vlw1o/image/upload/v1723963545/tg20vzmknpjwpvwek0be.png',
                 password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                 user_role=UserRole.ADMIN)
        u2 = User(name='nhat', username='nhat',
                  avatar='https://res.cloudinary.com/dzo5vlw1o/image/upload/v1723963545/tg20vzmknpjwpvwek0be.png',
                  password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                  user_role=UserRole.USER)
        u3 = User(name='QL', username='QL',
                  avatar='https://res.cloudinary.com/dzo5vlw1o/image/upload/v1723963545/tg20vzmknpjwpvwek0be.png',
                  password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                  user_role=UserRole.MANAGER)
        db.session.add_all([u, u2, u3])
        db.session.commit()
