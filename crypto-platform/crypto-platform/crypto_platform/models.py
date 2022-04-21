from crypto_platform import db
from sqlalchemy.sql import func

# User Table
class UserModel(db.Model):
    id = db.Column(db.String(36), primary_key=True) # The string will be a UUID, which has 36 characters
    email = db.Column(db.String(), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

# Basket Tables
class BasketModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    description = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class BasketCryptoPercentageModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    basket_id = db.Column(db.Integer, db.ForeignKey(BasketModel.id), nullable=False)
    crypto = db.Column(db.String(), nullable=False)
    percentage = db.Column(db.Float(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class UserBasketModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey(UserModel.id), nullable=False)
    basket_id = db.Column(db.Integer, db.ForeignKey(BasketModel.id), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class UserBasketCryptoAmountModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey(UserModel.id), nullable=False)
    basket_id = db.Column(db.Integer, db.ForeignKey(BasketModel.id), nullable=False)
    crypto = db.Column(db.String(), nullable=False)
    amount = db.Column(db.Float(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

# Failed Transaction Tables
class FailedBuyModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey(UserModel.id), nullable=False)
    basket_id = db.Column(db.Integer, db.ForeignKey(BasketModel.id), nullable=False)
    crypto = db.Column(db.String(), nullable=False)
    buy_amount = db.Column(db.Float(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

class FailedSellModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey(UserModel.id), nullable=False)
    basket_id = db.Column(db.Integer, db.ForeignKey(BasketModel.id), nullable=False)
    user_basket_crypto_amount_id = db.Column(db.Integer, db.ForeignKey(UserBasketCryptoAmountModel.id), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
