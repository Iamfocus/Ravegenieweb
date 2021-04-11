import requests
import logging
from threading import Thread
from ..exceptions import PaymentException

class FlutterService:
	INIT_REQUIREMENTS = set(('amount', 'customer_email', 'currency', 'txref'))

	def __init__(self, pub_key, secret_key, redirect_url, init_url, verif_url, init_reqs=None, logger=None):
		self.pub_key = pub_key
		self.secret_key = secret_key
		self.redirect_url = redirect_url
		self.init_url = init_url
		self.verif_url = verif_url
		self.init_requirements = set(init_reqs) if init_reqs else self.__class__.INIT_REQUIREMENTS
		self.logger = logger or logging.getLogger('flutter')
	
	def _log_response(self, response):
		self._log(response.text)
	
	def _log(self, message):
		Thread(target=self.logger.info, args=[message]).start()

	def _get_payment_init_options(self, **kwargs):	
		if self.init_requirements != set(kwargs.keys()):
			raise PaymentException("Invalid parameters passed for FlutterWave")
		init_options = {
			'PBFPubKey': self.pub_key,
			'redirect_url': self.redirect_url,
		}
		init_options.update(kwargs)
		return init_options

	def init_payment(self, **kwargs):
		init_url = self.init_url 
		init_options = self._get_payment_init_options(**kwargs)
		response = requests.post(
			init_url,
			json=init_options,
			headers={"content-type": "application/json", "cache-control": "no-cache"}
		)
		if response.status_code != 200:
			raise PaymentException("Could not connect to FlutterWave")
		try:
			json_response = response.json()
		except ValueError:
			raise PaymentException("Invalid data received from FlutterWave")
		if not json_response['data'] or not json_response['data']['link']:
			self._log(json_response['message'])
			raise PaymentException(json_response['message'])
		return json_response['data']['link']

	def verify_payment(self, txref, amount, currency):
		verify_url = self.verif_url 
		verification_data = {
			'txref': txref,
			'SECKEY': self.secret_key
		}
		response = requests.post(
			verify_url,
			json=verification_data,
			headers={"content-type": "application/json"}
		)
		if response.status_code != 200:
			return False
		json_response = response.json()
		if (
			json_response['data']['status'] != 'successful' or not
			(
				json_response['data']['chargecode'] == '00' or 
				json_response['data']['chargecode'] == '0'
			)
		):
			return False
		if (
			json_response['data']['amount'] == amount and 
			json_response['data']['currency'] == currency and 
			json_response['data']['txref'] == txref
		):
			self._log_response(response)
			return True
		return False
