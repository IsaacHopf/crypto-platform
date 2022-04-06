"""Scripts for handling notifications."""

from crypto_platform.models import UserModel

from crypto_platform import mail
from flask_mail import Message

def get_all_emails():
	"""Gets the email of every user in the database."""
	all_users = UserModel.query.all()
	all_emails = []

	for user in all_users:
		all_emails.append(user.email)

	return all_emails

def send_tax_loss_harvest_notifications():
	"""Sends an email notification informing all users of potential for tax loss harvesting."""
	recipients = get_all_emails()

	with mail.connect() as conn:
		for recipient in recipients:
			message = "Hello, your account has potential for tax loss harvesting. Please log in to check."
			subject = "Tax Loss Harvesting Potential"
			msg = Message(recipients=[recipient],
						  body=message,
						  subject=subject)
			conn.send(msg)

def send_transaction_error_notification(recipient, e):
	msg = Message("An Error Occurred with your Transaction",
				  recipients=[recipient])
	msg.body = "An error occurred while processing your transaction. Error Code: " + str(e) + ". Please contact support to proceed."
	mail.send(msg)
