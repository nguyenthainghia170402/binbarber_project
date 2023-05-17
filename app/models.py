from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from app import db, login_manager


class Customer(UserMixin, db.Model):
    __tablename__ = 'customers'

    customerid = db.Column(db.Integer, primary_key=True)
    customername = db.Column(db.String(60))
    birthday = db.Column(db.Date)
    phonenumber = db.Column(db.String(13))
    account = db.Column(db.String(60), unique=True)
    password_hash = db.Column(db.String(128))
    isadmin = db.Column(db.Boolean, default=False)
    createat = db.Column(db.DateTime, default=datetime.now())
    updateat = db.Column(db.DateTime, onupdate=datetime.now())
    hide = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='customer', lazy='dynamic')

    # def __init__(self, customername, birthday, phonenumber, account, password):
    #     self.customername = customername
    #     self.birthday = birthday
    #     self.phonenumber = phonenumber
    #     self.account = account

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return (self.customerid)

    def __repr__(self):
        return f"({self.customerid}) {self.customername}"

    # Set up user_loader


@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))


class Barber(db.Model):
    __tablename__ = 'barbers'

    barberid = db.Column(db.Integer, primary_key=True)
    barbername = db.Column(db.String(30))
    birthday = db.Column(db.DateTime)
    address = db.Column(db.String(50))
    phonenumber = db.Column(db.String(13))
    forte = db.Column(db.String(50))
    description = db.Column(db.String(1000))
    image = db.Column(db.String(300))
    createat = db.Column(db.DateTime, default=datetime.now())
    updateat = db.Column(db.DateTime, onupdate=datetime.now())
    hide = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='barber', lazy='dynamic')

    worktimes = db.relationship('WorkTime', backref='barberWTime', lazy='dynamic')
    cusimages = db.relationship('CustomerImage', backref='barberCIma', lazy='dynamic')

    # def __init__(self, barberid, barbername, birthday, address, phonenumber, forte, description, image):
    #     self.barberid = barberid
    #     self.fullname = barbername
    #     self.birthday = birthday
    #     self.address = address
    #     self.phonenumber = phonenumber
    #     self.forte = forte
    #     self.description = description
    #     self.image = image

    def __repr__(self):
        return f"({self.barberid}) {self.barbername}"


service_booking = db.Table('service_booking',
                           db.Column('bookingid', db.Integer, db.ForeignKey('bookings.bookingid')),
                           db.Column('serviceid', db.Integer, db.ForeignKey('services.serviceid'))
                           )


class Booking(db.Model):
    __tablename__ = 'bookings'

    bookingid = db.Column(db.Integer, primary_key=True)
    customerid = db.Column(db.Integer, db.ForeignKey('customers.customerid'))
    barberid = db.Column(db.Integer, db.ForeignKey('barbers.barberid'))
    bookingdate = db.Column(db.Date)
    bookingtime = db.Column(db.Time)
    state = db.Column(db.String(20))
    createat = db.Column(db.DateTime, default=datetime.now())
    updateat = db.Column(db.DateTime, onupdate=datetime.now())
    hide = db.Column(db.Boolean, default=False)

    booked_services = db.relationship('Service', secondary=service_booking, backref='booked')

    # def __init__(self, bookingid, customerid, barberid, bookingtime, state):
    #     self.bookingid = bookingid
    #     self.customerid = customerid
    #     self.barberid = barberid
    #     self.bookingtime = bookingtime
    #     self.state = state

    def __repr__(self):
        return f"({self.bookingid}) {self.customerid} {self.barberid} {self.state}"


class Service(db.Model):
    __tablename__ = 'services'

    serviceid = db.Column(db.Integer, primary_key=True)
    servicename = db.Column(db.String(50), unique=True)
    timeofservice = db.Column(db.Integer)
    price = db.Column(db.BigInteger)
    createat = db.Column(db.DateTime, default=datetime.now())
    updateat = db.Column(db.DateTime, onupdate=datetime.now())
    hide = db.Column(db.Boolean, default=False)

    # def __init__(self, serviceid, servicename, timeofservice, price):
    #     self.serviceid = serviceid
    #     self.servicename = servicename
    #     self.timeofservice = timeofservice
    #     self.price = price

    def __repr__(self):
        return f"({self.serviceid}) {self.servicename} {self.timeofservice} {self.price}"


class WorkTime(db.Model):
    __tablename__ = 'worktime'

    worktimeid = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    timefrom = db.Column(db.Time)
    timeto = db.Column(db.Time)
    statework = db.Column(db.String(30))
    createat = db.Column(db.DateTime, default=datetime.now())
    updateat = db.Column(db.DateTime, onupdate=datetime.now())

    barberid = db.Column(db.Integer, db.ForeignKey('barbers.barberid'))

    # def __init__(self, worktimeid, date, timefrom, timeto, statework, barberid):
    #     self.worktimeid = worktimeid
    #     self.date = date
    #     self.timefrom = timefrom
    #     self.timeto = timeto
    #     self.statework = statework
    #     self.barberid = barberid

    def __repr__(self):
        return f"({self.worktimeid}) {self.date} {self.timefrom} {self.timeto} {self.statework} {self.barberid}"


class CustomerImage(db.Model):
    __tablename__ = 'customerimages'

    cusimageid = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(300))
    createat = db.Column(db.DateTime, default=datetime.now())
    updateat = db.Column(db.DateTime, onupdate=datetime.now())

    barberid = db.Column(db.Integer, db.ForeignKey('barbers.barberid'))

    # def __init__(self, cusimageid, image, barberid):
    #     self.cusimageid = cusimageid
    #     self.image = image
    #     self.barberid = barberid

    def __repr__(self):
        return f"({self.cusimageid}) {self.image} {self.barberid}"


class Blog(db.Model):
    __tablename__ = 'blogs'

    blogid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    subtitle = db.Column(db.String(80), unique=True)
    content = db.Column(db.String(1000))
    postdate = db.Column(db.DateTime)

    def __init__(self, blogid, title, subtitle, content, postdate):
        self.blogid = blogid
        self.title = title
        self.subtitle = subtitle
        self.content = content
        self.postdate = postdate

    def __repr__(self):
        return f"({self.blogid}) {self.postdate}"
