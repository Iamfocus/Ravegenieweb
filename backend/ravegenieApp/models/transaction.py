from django.db import models
from utils.models import ModelMixin
from django.contrib.auth import get_user_model
from .user import User
from django.conf import settings


class Transaction(models.Model, ModelMixin):
	
	DEPOSIT = 'DP'
	WITHDRAWAL = 'WD'
	BONUS = 'BO'
	DEBIT = "DB"
	CREDIT = "CR"

	SUCCESSFUL = 'SU'
	FAILED = 'FA'
	PENDING = 'PN'

	TRANSACTION_STATES = (
		(PENDING, "Pending"),
		(SUCCESSFUL, "Successful"),
		(FAILED, "Failed")
	)
	TRANSACTION_TYPES = (
		(WITHDRAWAL, "Withdrawal"),
		(DEPOSIT, "Deposit"),
		(BONUS, "Bonus"),
		(DEBIT, "Debit"),
		(CREDIT, "Credit")
	)

	type = models.CharField(max_length=2, choices=TRANSACTION_TYPES, db_index=True)
	created_at = models.DateTimeField(auto_now_add=True)
	modified_on = models.DateTimeField(auto_now=True)
	status = models.CharField(max_length=2, choices=TRANSACTION_STATES, default=PENDING,  db_index=True)
	dollar_amount = models.DecimalField(default=0, decimal_places=2, max_digits=10)
	naira_amount = models.DecimalField(default=0, decimal_places=2, max_digits=10)
	user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='transactions')
	comment = models.CharField(max_length=60, null=True)

	def get_dict(self):
		return {
			'type': self.type,
			'createdAt': self.get_time_string(self.created_at),
			'modifiedOn': self.get_time_string(self.modified_on),
			'status': self.status,
			'dollarAmount': self.dollar_amount,
			'nairaAmount': self.naira_amount,
			'user': str(self.user),
			'comment': self.comment
		}
	
	def save(self, *args, **kwargs):
		if not self.naira_amount:
			self.naira_amount = settings.TO_NAIRA(self.dollar_amount)
		super().save(*args, **kwargs)