from ..services import FlutterPaymentService
from ..exceptions import PaymentException

class PaymentFactory:
	AVAILABE_SERVICES = {
		'FLUTTER': FlutterPaymentService,
	}
	@classmethod
	def get_service(cls, service_name):
		service_name = service_name.upper()
		available_services = cls.AVAILABLE_SERVICES
		try:
			service = available_services['service_name']
		except KeyError:
			raise PaymentException
		return service