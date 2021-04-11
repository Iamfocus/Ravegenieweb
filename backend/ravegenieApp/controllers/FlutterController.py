from utils.controller import Controller
from utils.shortcuts import json_response
from ..services import FlutterPaymentService
from django.shortcuts import redirect
from ..models import Transaction
from django.conf import settings
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

class FlutterController(Controller):


	@Controller.route("redirect")
	def flutter_redirect(self, request):
		txref = request.GET.get('txref', None)
		if not txref:
			redirect(settings.PAYMENT_FAILURE_URL)
		if self.verify_transaction(txref):
			redirect(settings.PAYMENT_SUCCESS_URL)
		else:
			redirect(settings.PAYMENT_FAILURE_URL)

	@Controller.route("hook")
	@Controller.decorate(require_POST, csrf_exempt)
	def flutter_webhook(self, request):
		their_signature = request.headers.get('verif-hash', None)
		my_signature = settings.FLUTTER_SIGNATURE
		if my_signature and their_signature and my_signature == their_signature:
			data = json.loads(request.body)
			txref = data.get('txref', None) or data.get('txRef', None)
			if not txref:
				return json_response()

			if self.verify_transaction(txref):
				return json_response()
			else:
				return json_response()
		return json_response(status=False)

	def verify_transaction(self, txref):
		payment_service = FlutterPaymentService()
		transaction = payment_service.get_trans_by_ref(txref)
		if not transaction:
			return False
		flutter_service = payment_service.get_verification_service()
		payment_status = flutter_service.verify_payment(
			txref=txref,
			amount=transaction.naira_amount,
			currency=settings.CURRENCY
		)
		if payment_status:
			transaction.status = Transaction.SUCCESSFUL
			transaction.save()
			return True
		else:
			return False
