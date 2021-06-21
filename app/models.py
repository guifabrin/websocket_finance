from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

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

    serialize_only = ('id', 'name', 'email', 'picture', 'created_at')


class Account(Base, SerializerMixin):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    is_credit_card = Column(Integer, server_default=text("'0'"))
    user_id = Column(ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    user = relationship('User', lazy='subquery')

    _transactions = relationship("Transaction", back_populates="account", lazy='subquery')
    invoices = relationship("Invoice", back_populates="account", lazy='subquery')

    serialize_only = ('id', 'description', 'is_credit_card', 'transactions', 'invoices')

    @property
    def transactions(self):
        if self.is_credit_card:
            return []
        else:
            return self._transactions


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
    date_init = Column(Date, nullable=False)
    date_end = Column(Date, nullable=False)
    debit_date = Column(Date, nullable=False)
    closed = Column(Integer, nullable=False, server_default=text("'0'"))
    account_id = Column(ForeignKey('accounts.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    account = relationship('Account', lazy='subquery')

    transactions = relationship("Transaction", back_populates="invoice", lazy='subquery')

    serialize_only = ('id', 'description', 'date_init', 'date_end', 'debit_date', 'transactions')

    @property
    def user(self):
        if self.account:
            return self.account.user
        return None

    @property
    def user_id(self):
        if self.user:
            return self.user.id
        return None


class Transaction(Base, SerializerMixin):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    value = Column(Float, nullable=False)
    paid = Column(Integer, nullable=False)
    account_id = Column(ForeignKey('accounts.id'), nullable=False)
    invoice_id = Column(ForeignKey('invoices.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)

    serialize_only = ('id', 'description', 'date', 'paid', 'value')

    account = relationship('Account', lazy='subquery')
    invoice = relationship('Invoice', lazy='subquery')

    @property
    def user(self):
        if self.account:
            return self.account.user
        return None

    @property
    def user_id(self):
        if self.user:
            return self.user.id
        return None

    def update(self, other):
        if other.paid:
            self.paid = other.paid


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