from django.test import TestCase
from utils.tests import TestMixin
from ..services import FlutterService
from django.conf import settings
from unittest.mock import patch, Mock
import requests
from ..exceptions import PaymentException
from faker import Faker

faker = Faker()
bad_json_data_message = faker.sentence()
init_link = faker.url()
bad_data_json_mock = Mock(**{
	'status_code': 200, 
	'json.return_value': {'data': None, 'message': bad_json_data_message}
	}
)
bad_json_link_response_mock = Mock(**{
	'status_code': 200,
	'json.return_value': {'data': {'link': None}, 'message': bad_json_data_message}
	}
)
init_works_mock = Mock(**{
	'status_code': 200, 
	'json.return_value': {'data': {'link': init_link}}
	}
)

verif_bad_status_mock = Mock(**{
	'status_code': 200,
	'json.return_value': {'data': {'status': 'bad'} }
 }
)

verif_bad_chargecode_mock = Mock(**{
	'status_code': 200,
	'json.return_value': {'data': {'status': 'successful', 'chargecode': '1'} }
	} )

verif_bad_amount_mock = Mock(**{
	'status_code': 200,
	'json.return_value': 
		{'data': 
			{'status': 'successful', 'chargecode': '00', 'amount': 30, 'currency': 'NGN', 'txref': 'ref'} 
		}
	} )

verif_bad_currency_mock = Mock(**{
	'status_code': 200,
	'json.return_value': 
		{'data': 
			{'status': 'successful', 'chargecode': '00', 'amount': 30, 'currency': 'USD', 'txref': 'ref'} 
		}
	} )

verif_bad_txref_mock = Mock(**{
	'status_code': 200,
	'json.return_value': 
		{'data': 
			{'status': 'successful', 'chargecode': '00', 'amount': 30, 'currency': 'NGN', 'txref': 'FAKE'} 
		}
	} )

verif_success_mock = Mock(**{
	'status_code': 200,
	'json.return_value': 
		{'data': 
			{'status': 'successful', 'chargecode': '00', 'amount': 30, 'currency': 'NGN', 'txref': 'ref'} 
		}
	} )

class TestFlutterService(TestCase, TestMixin):
	
	def setUp(self):
		self.service: FlutterService = FlutterService(
			pub_key=settings.FL_PUB_KEY,
			secret_key=settings.FL_SECRET_KEY,
			redirect_url=settings.FL_REDIRECT_URL,
			init_url=settings.FL_INIT_URL,
			verif_url=settings.FL_VERIFICATION_URL,
			init_reqs=None
		)
		self.faker = Faker()

	@patch.object(requests, 'post', return_value=Mock(**{'status_code': 400}))
	def test_init_payment_response_status_fail(self, mock):
		init_params = {
			'currency': "NGN",
			'txref': self.faker.word(),
			'customer_email': self.faker.email(),
			'amount': self.faker.random_number()
		}
		with self.assertRaises(PaymentException):
			self.service.init_payment(**init_params)
	
	def test_init_payment_param_fail(self):
		init_params = {
			'currency': "NGN",
			'txref': self.faker.word(),
			'customer_email': self.faker.email(),
		}
		with self.assertRaises(PaymentException):
			self.service.init_payment(**init_params)
		init_params = {
			'currency': "NGN",
			'txref': self.faker.word(),
			'customer_email': self.faker.email(),
			'amount': self.faker.random_number(),
			'url': self.faker.url()
		}
		with self.assertRaises(PaymentException):
			self.service.init_payment(**init_params)
		init_params = {}
		with self.assertRaises(PaymentException):
			self.service.init_payment(**init_params)
	
	@patch.object(requests, 'post', return_value=bad_data_json_mock)
	def test_bad_json_data_response(self, mock):
		init_params = {
			'currency': "NGN",
			'txref': self.faker.word(),
			'customer_email': self.faker.email(),
			'amount': self.faker.random_number()
		}
		with self.assertRaises(PaymentException) as exc:
			self.service.init_payment(**init_params)
			self.assertEqual(str(exc), bad_json_data_message)
	
	@patch.object(requests, 'post', return_value=bad_json_link_response_mock)
	def test_bad_json_link_response(self, mock):
		init_params = {
			'currency': "NGN",
			'txref': self.faker.word(),
			'customer_email': self.faker.email(),
			'amount': self.faker.random_number()
		}
		with self.assertRaises(PaymentException) as exc:
			self.service.init_payment(**init_params)
			self.assertEqual(str(exc), bad_json_data_message)

	@patch.object(requests, 'post', return_value=init_works_mock)
	def test_init_works(self, mock):
		init_params = {
			'currency': "NGN",
			'txref': self.faker.word(),
			'customer_email': self.faker.email(),
			'amount': self.faker.random_number()
		}	
		gate_way_url = self.service.init_payment(**init_params)
		self.assertEqual(gate_way_url, init_link)
	
	@patch.object(requests, 'post', return_value=Mock(status_code=289))
	def test_verification_with_bad_response(self, mock):
		verif_params = {
			'currency': "NGN",
			'txref': self.faker.word(),
			'amount': self.faker.random_number()
		}
		status = self.service.verify_payment(**verif_params)
		self.assertFalse(status)
	
	@patch.object(requests, 'post', return_value=verif_bad_status_mock)
	def test_verification_bad_status(self, mock):
		verif_params = {
			'currency': "NGN",
			'txref': self.faker.word(),
			'amount': self.faker.random_number()
		}
		status = self.service.verify_payment(**verif_params)
		self.assertFalse(status)
	
	@patch.object(requests, 'post', return_value=verif_bad_chargecode_mock)
	def test_verification_bad_chargecode(self, mock):
		verif_params = {
			'currency': "NGN",
			'txref': self.faker.word(),
			'amount': self.faker.random_number()
		}
		status = self.service.verify_payment(**verif_params)
		self.assertFalse(status)
	
	@patch.object(requests, 'post', return_value=verif_bad_amount_mock)
	def test_verification_bad_amount(self, mock):
		verif_params = {
			'currency': "NGN",
			'txref': 'ref',
			'amount': 100
		}
		status = self.service.verify_payment(**verif_params)
		self.assertFalse(status)

	@patch.object(requests, 'post', return_value=verif_bad_currency_mock)
	def test_verification_bad_currency(self, mock):
		verif_params = {
			'currency': "NGN",
			'txref': 'ref',
			'amount': 30
		}
		status = self.service.verify_payment(**verif_params)
		self.assertFalse(status)
	
	@patch.object(requests, 'post', return_value=verif_bad_txref_mock)
	def test_verification_bad_txref(self, mock):
		verif_params = {
			'currency': "NGN",
			'txref': 'ref',
			'amount': 30
		}
		status = self.service.verify_payment(**verif_params)
		self.assertFalse(status)

	@patch.object(requests, 'post', return_value=verif_success_mock)
	def test_verification_success(self, mock):
		verif_params = {
			'currency': "NGN",
			'txref': 'ref',
			'amount': 30
		}
		status = self.service.verify_payment(**verif_params)
		self.assertTrue(status)


	

