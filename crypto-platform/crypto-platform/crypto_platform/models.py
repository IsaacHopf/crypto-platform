from crypto_platform import db
from sqlalchemy.sql import func

class UserModel(db.Model):
    id = db.Column(db.String(36), primary_key=True) # The string will be a UUID, which has 36 characters
    email = db.Column(db.String, unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class FailedBuyModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey(UserModel.id))
    crypto = db.Column(db.String())
    buy_amount = db.Column(db.Float())
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class FailedSellModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey(UserModel.id))
    crypto = db.Column(db.String())
    sell_amount = db.Column(db.Float())
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
