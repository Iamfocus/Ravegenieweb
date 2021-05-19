from utils.controller import Controller
from utils.shortcuts import json_response
from utils.decorators import ensure_signed_in
from ..services import TransactionService
from ..factories import PaymentFactory
from .. import forms
from django.conf import settings
from ..exceptions import PaymentException
from ..models import Transaction
from rest_framework.decorators import api_view
from ..models import Transaction
from rest_framework.decorators import api_view

class TransactionController(Controller):

	def __init__(self):
		self.transaction_service = TransactionService()	

	@Controller.route("deposit/<str:service_name>")
	@Controller.decorate(api_view(['POST']), ensure_signed_in)
	def deposit(self, request, service_name):
		deposit_form = forms.DepositForm(request.data)
		self.validate_form(deposit_form)
		payment_service = PaymentFactory.get_service(service_name)(Transaction)
		transaction, txref = payment_service.create_deposit(
			type=Transaction.DEPOSIT,
			user=request.user,
			comment=service_name,
			dollar_amount=deposit_form.cleaned_data['amount']
		)
		try:
			gateway_url = payment_service.get_payment_provider().init_payment(
				amount=str(transaction.naira_amount),
				currency=settings.CURRENCY,
				customer_email=request.user.email,
				txref=txref
			)
		except PaymentException as e:
			transaction.status = Transaction.FAILED
			transaction.save()
			return json_response(status=False, error=str(e))
		else:
			return json_response(status=True, data={'redirectTo': gateway_url})

	
	@Controller.route()
	@Controller.decorate(api_view(['GET']), ensure_signed_in)
	def ping(self, request):
		transactions = request.user.transactions.all()
		transaction_details = [transaction.get_dict() for transaction in transactions]
		profile = request.user.get_profile()
		account_balance = profile.account_balance
		bonus_balance = profile.bonus_balance
		return json_response(True, data={
			'transactionHistory': transaction_details, 
			'accountBalance': account_balance, 
			'bonusBalance': bonus_balance
			}
		)
	
	@Controller.route()
	@Controller.decorate(ensure_signed_in)
	def redeem_bonus(self, request):
		publisher = request.user.publisher
		self.transaction_service.redeem_bonus(publisher)
		return json_response(True)
	
	@Controller.route()
	@Controller.decorate(ensure_signed_in)
	def withdraw(self, request):
		pass