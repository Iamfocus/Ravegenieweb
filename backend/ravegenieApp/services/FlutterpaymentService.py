from .PaymentService import PaymentService
from django.conf import settings
from .FlutterService import FlutterService

class FlutterPaymentService(PaymentService):
	def __get_flutter_instance(self, params):
		return self._provider or FlutterService(
			pub_key=settings.FL_PUB_KEY,
			secret_key=settings.FL_SECRET_KEY,
			redirect_url=settings.FL_REDIRECT_URL,
			init_url=settings.FL_INIT_URL,
			verif_url=settings.FL_VERIFICATION_URL,
			init_reqs=params
		)

	def get_verification_provider(self):
		return self.__get_flutter_instance(None)

	def get_payment_provider(self, params=None):
		return self.__get_flutter_instance(params)

