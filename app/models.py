from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from .database.database import Base


class Config(Base, SerializerMixin):
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)


class LtmTranslation(Base, SerializerMixin):
    __tablename__ = 'ltm_translations'

    id = Column(Integer, primary_key=True)
    status = Column(Integer, nullable=False, server_default=text("'0'"))
    locale = Column(String, nullable=False)
    group = Column(String, nullable=False)
    key = Column(String, nullable=False)
    value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)


class Permission(Base, SerializerMixin):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    description = Column(String)
    model = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)


class Role(Base, SerializerMixin):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    description = Column(String)
    level = Column(Integer, nullable=False, server_default=text("'1'"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)


class User(Base, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    picture = Column(String)
    remember_token = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    roles = relationship("RoleUser", back_populates="user", lazy='subquery')
    accounts = relationship("Account", back_populates="user", lazy='subquery')
    configs = relationship("UserConfig", back_populates="user", lazy='subquery')

    serialize_only = ('id', 'name', 'email', 'picture', 'created_at', 'configs')


class Account(Base, SerializerMixin):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    is_credit_card = Column(Integer, server_default=text("'0'"))
    ignore = Column(Integer, server_default=text("'0'"))
    user_id = Column(ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    automated_args = Column(String, nullable=False)
    automated_body = Column(Integer, server_default=text("'0'"))
    prefer_debit_account_id = Column(ForeignKey('accounts.id'), nullable=True)

    user = relationship('User', lazy='subquery')

    transactions = relationship("Transaction", back_populates="account", lazy='subquery')
    invoices = relationship("Invoice", back_populates="account", lazy='subquery')

    serialize_only = ('id', 'description', 'is_credit_card', 'automated_body', 'ignore', 'prefer_debit_account_id', 'automated_ref')

    @property
    def automated_ref(self):
        if self.automated_args is not None:
            return self.automated_args.split(',')[0]
        return False

    @property
    def sort_sum(self):
        suma = 0.2 if self.is_credit_card  else 0.1
        sumb = self.prefer_debit_account_id  if self.is_credit_card  else self.id
        sumc = 1000 if self.ignore else 0
        return -1* (suma + sumb + sumc)

class Category(Base, SerializerMixin):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    user = relationship('User', lazy='subquery')


class PermissionRole(Base, SerializerMixin):
    __tablename__ = 'permission_role'

    id = Column(Integer, primary_key=True)
    permission_id = Column(ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False, index=True)
    role_id = Column(ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    permission = relationship('Permission', lazy='subquery')
    role = relationship('Role', lazy='subquery')


class PermissionUser(Base, SerializerMixin):
    __tablename__ = 'permission_user'

    id = Column(Integer, primary_key=True)
    permission_id = Column(ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    permission = relationship('Permission', lazy='subquery')
    user = relationship('User', lazy='subquery')


class RoleUser(Base, SerializerMixin):
    __tablename__ = 'role_user'

    id = Column(Integer, primary_key=True)
    role_id = Column(ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    role = relationship('Role', lazy='subquery')
    user = relationship('User', lazy='subquery')

    serialize_only = ('role',)


class UserConfig(Base, SerializerMixin):
    __tablename__ = 'user_configs'
    __table_args__ = (
        Index('user_configs_user_id_config_id_unique', 'user_id', 'config_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    config_id = Column(ForeignKey('configs.id'), nullable=False)
    value = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    config = relationship('Config', lazy='subquery')
    user = relationship('User', lazy='subquery')

    serialize_only = ('config', 'value')

    def update(self, obj_values):
        self.value = obj_values['value']


class UserOauth(Base, SerializerMixin):
    __tablename__ = 'user_oauths'

    id = Column(Integer, primary_key=True)
    provider = Column(String, nullable=False)
    uuid = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    avatar = Column(String, nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    user = relationship('User', lazy='subquery')


class Invoice(Base, SerializerMixin):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    automated_id = Column(String, nullable=True)
    date_init = Column(Date, nullable=False)
    date_end = Column(Date, nullable=False)
    debit_date = Column(Date, nullable=False)
    closed = Column(Integer, nullable=False, server_default=text("'0'"))
    account_id = Column(ForeignKey('accounts.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    account = relationship('Account', lazy='subquery')

    transactions = relationship("Transaction", back_populates="invoice", lazy='subquery')

    serialize_only = ('id', 'description', 'date_init', 'date_end', 'debit_date', 'automated_id', 'total', 'total_positive', 'total_negative', 'account')

    def before_invoice(self):
        invoices = list(filter(lambda invoice: invoice.debit_date < self.debit_date, self.account.invoices))
        if len(invoices) == 0:
            return None
        return invoices[0]

    @property
    def total(self):
        invoice = self.before_invoice()
        return sum(map(lambda t: t.value, self.transactions)) + (invoice.total if invoice is not None else 0)

    @property
    def total_positive(self):
        return sum(map(lambda t: t.value, filter(lambda t: t.value > 0, self.transactions)))

    @property
    def total_negative(self):
        return sum(map(lambda t: t.value, filter(lambda t: t.value < 0, self.transactions)))

    @property
    def user(self):
        return self.account.user


class Transaction(Base, SerializerMixin):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    automated_id = Column(String, nullable=True)
    date = Column(Date, nullable=False)
    value = Column(Float, nullable=False)
    paid = Column(Integer, nullable=False)
    account_id = Column(ForeignKey('accounts.id'), nullable=False)
    invoice_id = Column(ForeignKey('invoices.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    serialize_only = ('id', 'description', 'date', 'paid', 'value', 'automated_id')

    account = relationship('Account', lazy='subquery')
    invoice = relationship('Invoice', lazy='subquery')

    def __init__(self):
        self.already_inserted = False

    @property
    def user(self):
        return self.account.user


class CategoryTransaction(Base, SerializerMixin):
    __tablename__ = 'category_transactions'
    __table_args__ = (
        Index('category_transactions_category_id_transaction_id_unique', 'category_id', 'transaction_id', unique=True),
    )

    id = Column(Integer, primary_key=True)
    category_id = Column(ForeignKey('categories.id'), nullable=False)
    transaction_id = Column(ForeignKey('transactions.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    category = relationship('Category', lazy='subquery')
    transaction = relationship('Transaction', lazy='subquery')

class Notification(Base, SerializerMixin):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    table = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    method = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    seen = Column(Integer, nullable=True, server_default=text("'0'"))

class Captha(Base, SerializerMixin):
    __tablename__ = 'captcha'

    id = Column(Integer, primary_key=True)
    base64_url = Column(String, nullable=False)
    result = Column(Integer, nullable=False)

    def update(self, obj_values):
        self.result = obj_values['value']

