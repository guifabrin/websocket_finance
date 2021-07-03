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

    serialize_only = ('id', 'name', 'email', 'picture', 'created_at')


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

    _transactions = relationship("Transaction", back_populates="account", lazy='subquery')
    invoices = relationship("Invoice", back_populates="account", lazy='subquery')

    serialize_only = (
        'id', 'description', 'is_credit_card', 'transactions', 'invoices', 'automated', 'automated_body', 'ignore')

    @property
    def transactions(self):
        if self.is_credit_card:
            return []
        else:
            return self._transactions

    def update(self, other):
        if hasattr(other, 'is_credit_card'):
            self.is_credit_card = 1 if other.is_credit_card else 0
        if hasattr(other, 'description') and len(other.description) > 0:
            self.description = other.description


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

    serialize_only = ('id', 'description', 'date_init', 'date_end', 'debit_date', 'transactions', 'automated_id')

    @property
    def str_debit_date(self):
        return self.debit_date.strftime("%Y-%m-%d")

    @str_debit_date.setter
    def str_debit_date(self, str_debit_date):
        self.debit_date = datetime.strptime(str_debit_date.split('T')[0], '%Y-%m-%d')

    @property
    def str_date_init(self):
        return self.date_init.strftime("%Y-%m-%d")

    @str_date_init.setter
    def str_date_init(self, str_date_init):
        self.date_init = datetime.strptime(str_date_init.split('T')[0], '%Y-%m-%d')

    @property
    def str_date_end(self):
        return self.date_end.strftime("%Y-%m-%d")

    @str_date_end.setter
    def str_date_end(self, str_date_end):
        self.date_end = datetime.strptime(str_date_end.split('T')[0], '%Y-%m-%d')

    @property
    def user(self):
        if self.account:
            return self.account.user
        return None

    @user.setter
    def user(self, user):
        pass

    @property
    def user_id(self):
        if self.user:
            return self.user.id
        return None

    def update(self, other):
        if hasattr(other, 'description'):
            self.description = other.description
        if hasattr(other, 'debit_date'):
            self.debit_date = other.debit_date
        if hasattr(other, 'date_init'):
            self.date_init = other.date_init
        if hasattr(other, 'date_end'):
            self.date_end = other.date_end

    @property
    def value(self):
        return sum(map(lambda t: t.value, self.transactions))


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
        if self.account:
            return self.account.user
        return None

    @user.setter
    def user(self, user):
        pass

    @property
    def str_date(self):
        return self.date.strftime("%Y-%m-%d")

    @str_date.setter
    def str_date(self, str_date):
        self.date = datetime.strptime(str_date.split('T')[0], '%Y-%m-%d')

    @property
    def user_id(self):
        if self.user:
            return self.user.id
        return None

    def update(self, other):
        if hasattr(other, 'paid'):
            self.paid = 1 if other.paid else 0
        if hasattr(other, 'description'):
            self.description = other.description
        if hasattr(other, 'date'):
            self.date = other.date
        if hasattr(other, 'invoice_id'):
            self.invoice_id = other.invoice_id
        if hasattr(other, 'value'):
            self.value = other.value


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
