from django.conf import settings
from django.utils import timezone
from datetime import timedelta

def yesterday():
	now = timezone.now()
	yesterday = now - timedelta(days=1)
	return yesterday
class MiscService:
	@classmethod
	def convert_to_naira(cls, dollar_amount):
		SDR = settings.SDR
		return SDR * dollar_amount
	
	@classmethod
	def convert_to_dollar(cls, naira_amount):
		SDR = settings.SDR
		return naira_amount / SDR	
