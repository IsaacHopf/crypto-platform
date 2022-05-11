"""
Database Models and CRUD scripts.
"""

from crypto_platform import db
from sqlalchemy.sql import func

"""User Table"""
class UserModel(db.Model):
    id = db.Column(db.String(36), primary_key=True) # The string will be a UUID, which has 36 characters
    email = db.Column(db.String(), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def add(id, email):
        new_user = UserModel(
            id = id,
            email = email
        )

        db.session.add(new_user)
        db.session.commit()

    def get_by_id(user_id):
        user = UserModel.query.filter_by(id = user_id).first()
        return user

    def update(user, email):
        user.email = email

        db.session.add(user)
        db.session.commit()

    def remove(user):
        db.session.delete(user)
        db.session.commit()

"""Basket Tables"""
class BasketModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    description = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def add(name, description):
        new_basket = BasketModel(
            name = name,
            description = description
        )

        db.session.add(new_basket)
        db.session.commit()

    def get_by_name(basket_name):
        basket = BasketModel.query.filter_by(name = basket_name).first()
        return basket

    def update(basket, name, description):
        basket.name = name
        basket.description = description

        db.session.add(basket)
        db.session.commit()

    def remove(basket):
        db.session.delete(basket)
        db.session.commit()

class BasketCryptoPercentageModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    basket_id = db.Column(db.Integer, db.ForeignKey(BasketModel.id), nullable=False)
    crypto = db.Column(db.String(), nullable=False)
    percentage = db.Column(db.Float(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def add(basket_id, crypto, percentage):
        new_basket_crypto_percentage = BasketCryptoPercentageModel(
            basket_id = basket_id,
            crypto = crypto,
            percentage = percentage
        )

        db.session.add(new_basket_crypto_percentage)
        db.session.commit()

    def get_all_by_basket(basket):
        crypto_percentages = BasketCryptoPercentageModel.query.filter_by(basket_id = basket.id).all()
        return crypto_percentages

    def update(basket_crypto_percentage, basket_id, crypto, percentage):
        basket_crypto_percentage.basket_id = basket_id
        basket_crypto_percentage.crypto = crypto
        basket_crypto_percentage.percentage = percentage

        db.session.add(basket_crypto_percentage)
        db.session.commit()

    def remove(basket_crypto_percentage):
        db.session.delete(basket_crypto_percentage)
        db.session.commit()

class UserBasketModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey(UserModel.id), nullable=False)
    basket_id = db.Column(db.Integer, db.ForeignKey(BasketModel.id), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def add(user, basket):
        new_user_basket = UserBasketModel(
            user_id = user.coinbase_id,
            basket_id = basket.id
        )

        db.session.add(new_user_basket)
        db.session.commit()

    def get_by_user_and_basket(user, basket):
        user_basket = UserBasketModel.query.filter_by(user_id = user.coinbase_id, basket_id = basket.id).first()
        return user_basket

    def update(user_basket, user_id, basket_id):
        user_basket.user_id = user_id
        user_basket.basket_id = basket_id

        db.session.add(user_basket)
        db.session.commit()

    def remove(user_basket):
        db.session.delete(user_basket)
        db.session.commit()

class UserBasketCryptoAmountModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey(UserModel.id), nullable=False)
    basket_id = db.Column(db.Integer, db.ForeignKey(BasketModel.id), nullable=False)
    crypto = db.Column(db.String(), nullable=False)
    amount = db.Column(db.Float(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def add(user, basket, crypto, amount):
        new_user_basket_crypto_amount = UserBasketCryptoAmountModel(
            user_id = user.coinbase_id,
            basket_id = basket.id,
            crypto = crypto,
            amount = amount
        )

        db.session.add(new_user_basket_crypto_amount)
        db.session.commit()

    def get_all_by_user_and_basket(user, basket):
        user_basket_crypto_amount = UserBasketCryptoAmountModel.query.filter_by(user_id = user.coinbase_id, basket_id = basket.id).all()
        return user_basket_crypto_amount

    def get_all_by_user_and_crypto(user, crypto):
        user_basket_crypto_amount = UserBasketCryptoAmountModel.query.filter_by(user_id = user.coinbase_id, crypto = crypto).all()
        return user_basket_crypto_amount

    def get_by_user_and_basket_and_crypto(user, basket, crypto):
        user_basket_crypto_amount = UserBasketCryptoAmountModel.query.filter_by(user_id = user.coinbase_id, basket_id = basket.id, crypto = crypto).first()
        return user_basket_crypto_amount

    def get_by_id(user_basket_crypto_amount_id):
        user_basket_crypto_amount = UserBasketCryptoAmountModel.query.get(user_basket_crypto_amount_id)
        return user_basket_crypto_amount

    def update(user_basket_crypto_amount, user_id, basket_id, crypto, amount):
        user_basket_crypto_amount.user_id = user_id
        user_basket_crypto_amount.basket_id = basket_id
        user_basket_crypto_amount.crypto = crypto
        user_basket_crypto_amount.amount = amount

        db.session.add(user_basket_crypto_amount)
        db.session.commit()

    def update_amount(user_basket_crypto_amount, amount):
        user_basket_crypto_amount.amount += amount

        db.session.add(user_basket_crypto_amount)
        db.session.commit()

    def remove(user_basket_crypto_amount):
        db.session.delete(user_basket_crypto_amount)
        db.session.commit()

"""Failed Transaction Tables"""
class FailedBuyModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey(UserModel.id), nullable=False)
    basket_id = db.Column(db.Integer, db.ForeignKey(BasketModel.id), nullable=False)
    crypto = db.Column(db.String(), nullable=False)
    buy_amount = db.Column(db.Float(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def add(user, basket, crypto, buy_amount):
        new_failed_buy = FailedBuyModel(
            user_id = user.coinbase_id,
            basket_id = basket.id,
            crypto = crypto,
            buy_amount = buy_amount
        )

        db.session.add(new_failed_buy)
        db.session.commit()

    def get_all_by_user_and_basket(user, basket):
        failed_buys = FailedBuyModel.query.filter_by(user_id = user.coinbase_id, basket_id = basket.id).all()
        return failed_buys

    def update(failed_buy, user_id, basket_id, crypto, buy_amount):
        failed_buy.user_id = user_id
        failed_buy.basket_id = basket_id
        failed_buy.crypto = crypto
        failed_buy.buy_amount = buy_amount

        db.session.add(failed_buy)
        db.session.commit()

    def remove(failed_buy):
        db.session.delete(failed_buy)
        db.session.commit()

class FailedSellModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey(UserModel.id), nullable=False)
    basket_id = db.Column(db.Integer, db.ForeignKey(BasketModel.id), nullable=False)
    user_basket_crypto_amount_id = db.Column(db.Integer, db.ForeignKey(UserBasketCryptoAmountModel.id), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def add(user, basket, user_basket_crypto_amount):
        new_failed_sell = FailedSellModel(
            user_id = user.coinbase_id,
            basket_id = basket.id,
            user_basket_crypto_amount_id = user_basket_crypto_amount.id
        )

        db.session.add(new_failed_sell)
        db.session.commit()

    def get_all_by_user_and_basket(user, basket):
        failed_sells = FailedSellModel.query.filter_by(user_id = user.coinbase_id, basket_id = basket.id).all()
        return failed_sells

    def update(failed_sell, user_id, basket_id, user_basket_crypto_amount_id):
        failed_sell.user_id = user_id
        failed_sell.basket_id = basket_id
        failed_sell.user_basket_crypto_amount_id = user_basket_crypto_amount_id

        db.session.add(failed_sell)
        db.session.commit()

    def remove(failed_sell):
        db.session.delete(failed_sell)
        db.session.commit()
