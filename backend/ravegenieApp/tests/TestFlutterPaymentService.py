from django.test import TestCase
from utils.tests import TestMixin
from ..services import FlutterPaymentService, FlutterService
from ..models import Transaction

class TestFlutterPaymentService(TestCase, TestMixin):
	
	def setUp(self):
		self.flutter_payment_service = FlutterPaymentService(Transaction)

	def test_get_payment_provider(self):
		payment_provider = self.flutter_payment_service.get_payment_provider()
		self.assertIsInstance(payment_provider, FlutterService)
	
	def test_get_verification_provider(self):
		verification_provider = self.flutter_payment_service.get_verification_provider()
		self.assertIsInstance(verification_provider, FlutterService)