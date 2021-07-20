import datetime

from sqlalchemy import Column, Date, Float, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

from .database.database import Base

class Config(Base, SerializerMixin):
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)


class User(Base, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    accounts = relationship(
        "Account",
        lazy='subquery',
        back_populates="user"
    )

    configs = relationship(
        "UserConfig",
        lazy='subquery',
        back_populates="user"
    )

    serialize_only = ('id', 'name', 'email', 'configs')


class Account(Base, SerializerMixin):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    is_credit_card = Column(Integer, server_default=text("'0'"))
    ignore = Column(Integer, server_default=text("'0'"))
    value_error = Column(Float, nullable=False)

    automated_args = Column(String, nullable=False)
    automated_body = Column(Integer, server_default=text("'0'"))
    prefer_debit_account_id = Column(ForeignKey('accounts.id'), nullable=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)

    user = relationship(
        'User',
        lazy='subquery',
        back_populates="accounts",
    )

    transactions = relationship(
        "Transaction",
        lazy='subquery',
        back_populates="account"
    )

    invoices = relationship(
        "Invoice",
        lazy='subquery',
        back_populates="account"
    )

    serialize_only = (
        'id', 'description', 'is_credit_card', 'automated_body', 'ignore', 'prefer_debit_account_id', 'automated_ref',
        'automated_args', 'sinvoices', 'value_error')

    @property
    def automated_ref(self):
        if self.automated_args is not None:
            return self.automated_args.split(',')[0]
        return False

    @property
    def sort_sum(self):
        suma = 0.2 if self.is_credit_card else 0.1
        sumb = self.prefer_debit_account_id if self.is_credit_card and self.prefer_debit_account_id else self.id
        sumc = 1000 if self.ignore else 0
        return -1 * (suma + sumb + sumc)

    def update(self, obj_value):
        self.description = obj_value['description']
        self.is_credit_card = obj_value['is_credit_card'] if 'is_credit_card' in obj_value else self.is_credit_card
        self.ignore = obj_value['ignore'] if 'ignore' in obj_value else self.ignore
        self.automated_args = obj_value['automated_args'] if 'ignore' in obj_value else self.automated_args
        self.automated_body = obj_value['automated_body'] if 'automated_body' in obj_value else self.automated_body
        self.prefer_debit_account_id = obj_value[
            'prefer_debit_account_id'] if 'prefer_debit_account_id' in obj_value else self.prefer_debit_account_id
        self.value_error = obj_value['value_error'] if 'value_error' in obj_value else self.value_error

    @property
    def sinvoices(self):
        return list(map(lambda invoice: {
            'id': invoice.id,
            'description': invoice.description
        }, self.invoices))


class UserConfig(Base, SerializerMixin):
    __tablename__ = 'user_configs'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    config_id = Column(ForeignKey('configs.id'), nullable=False)
    value = Column(Text)

    config = relationship('Config', lazy='subquery')
    user = relationship('User', lazy='subquery')

    serialize_only = ('config', 'value')

    def update(self, obj_values):
        self.value = obj_values['value']


class Invoice(Base, SerializerMixin):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    automated_id = Column(String, nullable=True)
    debit_date = Column(Date, nullable=False)
    account_id = Column(ForeignKey('accounts.id'), nullable=False)

    account = relationship('Account', lazy='subquery',
                           back_populates="invoices",
                           )

    transactions = relationship("Transaction", back_populates="invoice", lazy='subquery',
                                cascade="all, delete", )

    serialize_only = (
        'id', 'description', 'debit_date', 'automated_id', 'total', 'total_positive',
        'total_negative', 'account')

    @property
    def total(self):
        return sum(map(lambda t: t.value, self.transactions))

    @property
    def total_positive(self):
        return sum(map(lambda t: t.value, filter(lambda t: t.value > 0, self.transactions)))

    @property
    def total_negative(self):
        return sum(map(lambda t: t.value, filter(lambda t: t.value < 0, self.transactions)))

    @property
    def user(self):
        return self.account.user

    def update(self, obj_values):
        self.description = obj_values['description'] if 'description' in obj_values else self.description
        self.debit_date = datetime.datetime.strptime(obj_values['debit_date'],
                                                     '%Y-%m-%d') if 'date' in obj_values else self.debit_date


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

    serialize_only = (
    'id', 'description', 'date', 'paid', 'value', 'automated_id', 'account_id', 'sinvoices', 'invoice_id')

    account = relationship('Account', lazy='subquery',
                           back_populates="transactions",
                           )
    invoice = relationship('Invoice', lazy='subquery',
                           back_populates="transactions",
                           )

    def __init__(self):
        self.already_inserted = False

    @property
    def user(self):
        return self.account.user

    def update(self, obj_values):
        self.paid = obj_values['paid'] if 'paid' in obj_values else self.paid
        self.value = obj_values['value'] if 'value' in obj_values else self.value
        self.invoice_id = obj_values['invoice_id'] if 'invoice_id' in obj_values else self.invoice_id
        self.date = datetime.datetime.strptime(obj_values['date'], '%Y-%m-%d') if 'date' in obj_values else self.date
        self.description = obj_values['description'] if 'description' in obj_values else self.description

    @property
    def sinvoices(self):
        if self.account.is_credit_card:
            return self.account.sinvoices
        return []


class Notification(Base, SerializerMixin):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    table = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    method = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    seen = Column(Integer, nullable=True, server_default=text("'0'"))

    def update(self, obj_values):
        if 'seen' in obj_values:
            self.seen = obj_values['seen']


class Captha(Base, SerializerMixin):
    __tablename__ = 'captcha'

    id = Column(Integer, primary_key=True)
    base64_url = Column(String, nullable=False)
    result = Column(Integer, nullable=False)

    def update(self, obj_values):
        self.result = obj_values['value']