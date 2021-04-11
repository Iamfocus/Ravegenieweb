from django.core import signing
import logging
from ..exceptions import PaymentException


Logger = logging.getLogger('ravegenie')

class PaymentService:
	

	def __init__(self, transaction_model, transaction=None, provider=None):
		self._transaction = transaction
		self._transaction_model = transaction_model
		self._provider = provider or None

	def create_deposit(self, *args, **kwargs):
		transaction = self._transaction_model.objects.create(*args, **kwargs)
		txref = self.get_ref_from_trans(transaction)
		return transaction, txref
	
	def get_ref_from_trans(self, trans):
		ref_tuple = (trans.pk,)
		txref = signing.dumps(ref_tuple)
		return txref

	def get_trans_by_ref(self, txref):
		ref_tuple = signing.loads(txref)
		try:
			transaction = self._transaction_model.objects.get(id=ref_tuple[0])
		except Exception as e:
			Logger.CRITICAL(e)
			return None
		else:
			return transaction
		
	def get_verification_provider(self):
		raise NotImplemented

	def get_payment_provider(self, params):
		raise NotImplemented

	
