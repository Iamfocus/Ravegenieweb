
from ..models import Transaction
from ..exceptions import TransactionError
from django.db import IntegrityError
from django.db.transaction import atomic
from django.db.models import F
import logging

Logger = logging.getLogger('ravegenieApp')


class TransactionService:
	def transact_subscription(self, account, principal, comment=''):
		self._debit_account(account, principal)
		Transaction.objects.create(
			user=account.user,
			type=Transaction.DEBIT,
			dollar_amount=principal,
			comment=comment
		)

	def credit(self, account, amount, comment=''):
		transaction = Transaction(
			type=Transaction.BONUS,
			status=Transaction.SUCCESSFUL,
			dollar_amount=amount,
			user=account.user,
			comment=comment
		)
		account.account_balance = F('account_balance') + amount
		return self._commit_transaction(account, transaction)

	def deposit_confirmed(self, transaction):
		account = transaction.user.get_profile()
		amount = transaction.dollar_amount
		account.account_balance = F('account_balance') + amount
		return self._commit_transaction(account, transaction)

	def create_bonus(self, account, amount, comment=''):
		transaction = Transaction(
			type=Transaction.BONUS,
			status=Transaction.SUCCESSFUL,
			dollar_amount=amount,
			user=account.user,
			comment=comment,
		)
		account.bonus_balance = F('bonus_balance') + amount
		return self._commit_transaction(account, transaction)
	
	def redeem_bonus(self, publisher):
		publisher.account_balance = F('account_balance') + F('bonus_balance')
		publisher.bonus_balance = 0
		publisher.save()

	def _commit_transaction(self, account, transaction):
		try:
			with atomic():
				transaction.save()
				account.save()
		except Exception as e:
			Logger.critical(e)
			return False
		else:
			return True

	def _debit_account(self, account, principal):
		if account.account_balance >= principal:
			account.account_balance = account.account_balance - principal
		elif account.bonus_balance >= principal:
			account.account_balance = account.bonus_balance - principal
		else:
			raise TransactionError("Insufficient balance")			
		try:
			account.save()
		except IntegrityError:
			raise TransactionError("Insufficient balance")
	
	def get_bonus_discounted_amount(self, percent, amount):
		return (percent / 100) * amount
