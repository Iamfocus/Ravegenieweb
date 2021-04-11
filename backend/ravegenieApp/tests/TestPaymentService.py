from django.test import TestCase
from utils.tests import TestMixin
from ..models import Transaction
from ..services import PaymentService
from django.contrib.auth import get_user_model
from django.core import signing

User = get_user_model()
class TestPaymentService(TestCase, TestMixin):
	
	def setUp(self):
		self.payment_service = PaymentService(Transaction)
		user_data = {
				'email': 'me@example.com', 
				'password': 'inlocoparentis156', 
				'first_name': 'hiz', 
				'last_name': 'dynasty'
		}
		self.user = User.objects.create(**user_data)
		self.user.set_password(user_data['password'])
	
	
	def test_create_deposit(self):
		transaction_data = {
			"type":Transaction.DEPOSIT,
			"user": self.user,
			"comment": "FLUTTER",
			"dollar_amount":2500,
		}		
		transaction, txref = self.payment_service.create_deposit(**transaction_data)
		self.assertTrue(isinstance(transaction, Transaction))
		self.assertEqual(transaction.type, transaction_data['type'])
		self.assertEqual(transaction.user, transaction_data['user'])
		self.assertEqual(transaction.dollar_amount, transaction_data['dollar_amount'])
	

	def test_transaction_matches_reference(self):
		transaction_data = {
			"type":Transaction.DEPOSIT,
			"user": self.user,
			"comment": "FLUTTER",
			"dollar_amount":2500,
		}		
		transaction, txref = self.payment_service.create_deposit(**transaction_data)
		ref_tuple = (transaction.pk,)
		test_ref = signing.dumps(ref_tuple)
		self.assertEqual(txref, test_ref)
		ref_tuple = signing.loads(txref)
		test_trans = Transaction.objects.get(id=ref_tuple[0])
		self.assertEqual(test_trans, transaction)
