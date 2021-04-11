from rest_framework.exceptions import APIException
class PaymentException(Exception):
	pass

class TransactionError(APIException):
	status_code = 200

class CampaignError(APIException):
	status_code = 400

class PromotionError(APIException):
	status_code = 400