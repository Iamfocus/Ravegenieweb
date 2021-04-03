from ..models import Campaign, CampaignSub
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import logging
from .MiscService import yesterday

Logger = logging.getLogger('ravegenieApp')

class CampaignsupervisorService:
	def clean(self):
		self._resolve_daily_subscriptions()
		self._resolve_monthly_subscriptions()
		self._delete_expired_campaigns()
		self._delete_expired_subscriptions()
	
	def _delete_expired_campaigns(self):
		query = Q(internal=False) and Q(end_date__lte=yesterday())
		try:
			Campaign.objects.filter(query).delete()
		except Exception as e:
			Logger.error(str(e))
	
	def _resolve_daily_subscriptions(self):
		query = Q(end_date__gte=timezone.now()) and Q(active_day_end__lte=timezone.now())
		subscriptions = CampaignSub.objects.filter(query)
		for subscription in subscriptions:
			subscription.reset_day()

	def _resolve_monthly_subscriptions(self):
		query = Q(end_date__lte=timezone.now())
		subscriptions = CampaignSub.objects.filter(query)
		for subscription in subscriptions:
			subscription.reset_month()
	
	def _delete_expired_subscriptions(self):
		CampaignSub.objects.filter(end_date__lte=yesterday()).exclude(active_days__icontains=False).delete()

	
	