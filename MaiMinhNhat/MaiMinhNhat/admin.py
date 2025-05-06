from typing import List

from flask_admin import Admin, expose, AdminIndexView, expose_plugview
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView
from flask_admin.helpers import get_url
from markupsafe import Markup

from MaiMinhNhat.models import Category, Product, UserRole,User,Receipt,ReceiptDetails,ORDER_STATUS_LABELS
from MaiMinhNhat import app, db, dao
from flask_login import logout_user, current_user
from flask import redirect, request, render_template, url_for
from datetime import datetime
from wtforms import TextAreaField
from wtforms.widgets import TextArea


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()



class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


class MyProductView(AuthenticatedView):
    column_list = ['id', 'name', 'category_id', 'price']
    column_searchable_list = ['id', 'name']
    column_filters = ['id', 'name', 'price']
    column_editable_list = ['name']
    can_export = True
    column_labels = {
        'name': 'Tên sản phẩm',
        'category_id': 'Danh mục',
        'price': 'Đơn giá'
    }

    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']
    form_overrides = {
        'description': CKTextAreaField
    }


class MyCategoryView(AuthenticatedView):
    column_list = ['id', 'name', 'products']

    def is_accessible(self):
        return (current_user.is_authenticated and
                (current_user.user_role == UserRole.ADMIN))

    def inaccessible_callback(self, name, **kwargs):
        # Nếu người dùng không có quyền, chuyển hướng đến trang "customer.html"
        if current_user.is_authenticated:
            return self.render('admin/customer.html')
        else:
            # Nếu người dùng chưa đăng nhập, chuyển hướng về trang đăng nhập
            return redirect(url_for('login_my_user', next=request.url))


class StatsView(BaseView):
    @expose('/')
    def index(self):
        revenue_by_prods = dao.stats_revenue_by_product(kw=request.args.get('kw'))
        revenue_by_period = dao.stats_revenue_by_period(year=request.args.get('year', datetime.now().year),
                                                        period=request.args.get('period', 'month'))

        return self.render('admin/stats.html',
                           revenue_by_prods=revenue_by_prods,
                           revenue_by_period=revenue_by_period)

    def is_accessible(self):
        return (current_user.is_authenticated and
                (current_user.user_role == UserRole.ADMIN))

    def inaccessible_callback(self, name, **kwargs):
        # Nếu người dùng không có quyền, chuyển hướng đến trang "customer.html"
        if current_user.is_authenticated:
            return self.render('admin/customer.html')
        else:
            # Nếu người dùng chưa đăng nhập, chuyển hướng về trang đăng nhập
            return redirect(url_for('login_my_user', next=request.url))


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/')


    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role != UserRole.USER

    def inaccessible_callback(self, name, **kwargs):
        # Nếu người dùng không có quyền, chuyển hướng đến trang "customer.html"
        if current_user.is_authenticated:
            return self.render('admin/customer.html')
        else:
            # Nếu người dùng chưa đăng nhập, chuyển hướng về trang đăng nhập
            return redirect(url_for('login_my_user', next=request.url))

# class MyAdminIndexView(AdminIndexView):
#     @expose('/')
#     def index(self):
#         stats = dao.count_products_by_cate()
#         return self.render('admin/index.html', stats=stats)
#
#
#     def is_accessible(self):
#         return (current_user.is_authenticated and
#                 (current_user.user_role == UserRole.ADMIN or current_user.user_role == UserRole.MANAGER))


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        # Hàm index chỉ hiển thị nội dung cho ADMIN hoặc MANAGER
        stats = dao.count_products_by_cate()
        return self.render('admin/index.html', stats=stats)

    def is_accessible(self):
        # Kiểm tra quyền truy cập chỉ cho phép ADMIN hoặc MANAGER
        return (current_user.is_authenticated and
                (current_user.user_role == UserRole.ADMIN or current_user.user_role == UserRole.MANAGER))

    def inaccessible_callback(self, name, **kwargs):
        # Nếu người dùng không có quyền, chuyển hướng đến trang "customer.html"
        if current_user.is_authenticated:
            return self.render('admin/customer.html')
        else:
            # Nếu người dùng chưa đăng nhập, chuyển hướng về trang đăng nhập
            return redirect(url_for('login_my_user', next=request.url))




# quan ly user
class MyUserView(AuthenticatedView):
    column_list = ['id', 'name', 'username', 'user_role']
    column_searchable_list = ['name', 'username']
    column_filters = ['id', 'name', 'user_role']
    column_editable_list = ['name', 'user_role']
    can_export = True
    column_labels = {
        'name': 'Tên người dùng',
        'username': 'Tên đăng nhập',
        'user_role': 'Vai trò người dùng'
    }

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        # Nếu người dùng không có quyền, chuyển hướng đến trang "customer.html"
        if current_user.is_authenticated:
            return self.render('admin/customer.html')
        else:
            # Nếu người dùng chưa đăng nhập, chuyển hướng về trang đăng nhập
            return redirect(url_for('login_my_user', next=request.url))


# quan ly khach hang
class MyCustomerView(MyUserView):
    def get_query(self):
        return self.session.query(self.model).filter(self.model.user_role == UserRole.USER)

    def is_accessible(self):
        return (current_user.is_authenticated and
                (current_user.user_role == UserRole.ADMIN or current_user.user_role == UserRole.MANAGER))

    def inaccessible_callback(self, name, **kwargs):
        # Nếu người dùng không có quyền, chuyển hướng đến trang "customer.html"
        if current_user.is_authenticated:
            return self.render('admin/customer.html')
        else:
            # Nếu người dùng chưa đăng nhập, chuyển hướng về trang đăng nhập
            return redirect(url_for('login_my_user', next=request.url))

# quan ly nhan vien
class MyManagerView(MyUserView):
    def get_query(self):
        # Chỉ lấy Employee
        return self.session.query(self.model).filter(self.model.user_role == UserRole.MANAGER)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        # Nếu người dùng không có quyền, chuyển hướng đến trang "customer.html"
        if current_user.is_authenticated:
            return self.render('admin/customer.html')
        else:
            # Nếu người dùng chưa đăng nhập, chuyển hướng về trang đăng nhập
            return redirect(url_for('login_my_user', next=request.url))


# quan ly don hang
class MyReceiptView(AuthenticatedView):
    column_list = ['id','name','phone','address', 'created_date', 'order_status', 'cash_option']
    can_view_details = True
    column_details_list = ['user_id','user.username', 'details']
    column_searchable_list = ['id', 'user_id']
    column_filters = ['id', 'user_id', 'created_date']
    column_editable_list = ['active']
    can_export = True
    can_delete = True
    column_labels = {
        'id': 'Mã đơn hàng',
        'user.username': 'Tên tài khoản',
        'user_id': 'Mã khách hàng',
        'created_date': 'Ngày mua hàng',
        'order_status': 'Trạng thái',
        'name': 'Tên người nhận',
        'phone': 'Số điện thoại',
        'details': 'Chi tiết đơn hàng',
        'address': 'địa chỉ',
        'cash_option': 'Phương thức thanh toán'
    }


    def _list_details(view, context, model, name):
        details = model.details
        return ', '.join([f"{detail.product.name} (Số lượng: {detail.quantity})" for detail in details])

    column_formatters = {
        'details': _list_details
    }


    def is_accessible(self):
        return (current_user.is_authenticated and
                (current_user.user_role == UserRole.ADMIN or current_user.user_role == UserRole.MANAGER))

    def inaccessible_callback(self, name, **kwargs):
        # Nếu người dùng không có quyền, chuyển hướng đến trang "customer.html"
        if current_user.is_authenticated:
            return self.render('admin/customer.html')
        else:
            # Nếu người dùng chưa đăng nhập, chuyển hướng về trang đăng nhập
            return redirect(url_for('login_my_user', next=request.url))


# quan ly chi tiet don hang
class MyReceiptDetailsView(AuthenticatedView):
    column_list = ['id', 'product.name','receipt_id','receipt.user.username', 'quantity',  'price', 'created_date' ]
    column_searchable_list = ['id']
    column_filters = ['id', 'created_date','receipt_id']
    column_editable_list = ['active']
    can_export = True
    column_labels = {
        'id': 'Receipt Details',
        'product.name': 'Tên sản phẩm',
        'receipt_id': 'Mã đơn hàng',
        'receipt.user.username': 'Tên khách hàng',
        'quantity': 'Số lượng',
        'price': 'Giá',
        'created_date': 'Ngày mua hàng',

    }

    def is_accessible(self):
        return (current_user.is_authenticated and
                (current_user.user_role == UserRole.ADMIN or current_user.user_role == UserRole.MANAGER))

    def inaccessible_callback(self, name, **kwargs):
        # Nếu người dùng không có quyền, chuyển hướng đến trang "customer.html"
        if current_user.is_authenticated:
            return self.render('admin/customer.html')
        else:
            # Nếu người dùng chưa đăng nhập, chuyển hướng về trang đăng nhập
            return redirect(url_for('login_my_user', next=request.url))


admin = Admin(app, name='CaBi House', template_mode='bootstrap4', index_view=MyAdminIndexView())
admin.add_view(MyCategoryView(Category, db.session, name='Danh mục'))
admin.add_view(MyProductView(Product, db.session, name='Sản phẩm'))
admin.add_view(MyUserView(User, db.session, name='Người Dùng'))
admin.add_view(MyReceiptView(Receipt, db.session, name='Đơn Hàng'))
admin.add_view(MyReceiptDetailsView(ReceiptDetails, db.session, name='Chi tiết Đơn hàng'))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))
