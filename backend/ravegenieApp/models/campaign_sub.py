from django.db import models
from utils.models import DictionaryField, ListField, ModelMixin
from .campaign import Campaign
from .publisher import Publisher
import collections
import time
from datetime import timedelta
from django.utils import timezone
import json
from .transaction import Transaction
from rest_framework.fields import DictField
import logging
from django.conf import settings

Logger = logging.getLogger('ravegenieApp')

class CampaignSub(models.Model, ModelMixin):

	SUBSCRIPTION = collections.namedtuple('SUBSCRIPTION', ['min', 'max', 'daily_growth_percent'])
	AVAILABLE_PLANS = {
		"BRONZE": SUBSCRIPTION(settings.TO_DOLLAR(2500), settings.TO_DOLLAR(5000), 4.5),
		"SILVER": SUBSCRIPTION(settings.TO_DOLLAR(5500), settings.TO_DOLLAR(8500), 5.0),
		"GOLD": SUBSCRIPTION(settings.TO_DOLLAR(9000), settings.TO_DOLLAR(12000), 5.4),
		"PLATINUM": SUBSCRIPTION(settings.TO_DOLLAR(12500), settings.TO_DOLLAR(15500), 5.7)
	}
	MINIMUM_SUB = AVAILABLE_PLANS["BRONZE"].min

	SUBSCRIPTION_DAYS = 30

	start_date = models.DateTimeField(auto_now_add=True)
	end_date = models.DateTimeField()
	campaign = models.ForeignKey(Campaign, on_delete=models.DO_NOTHING, null=True, related_name='subscriptions')
	active_days = DictionaryField(max_length=1000, default={})
	active_day_end = models.DateTimeField(null=True)
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='campaign_subs')
	principal = models.DecimalField(decimal_places=2, max_digits=10)
	created_at = models.DateTimeField(auto_now_add=True)
	campaign_type = models.CharField(max_length=3, choices=Campaign.CAMPAIGN_TYPES, db_index=True)

	class Meta:
		ordering = ['-start_date']
 
	def get_dict(self):
		return {
			'startDate': self.get_time_string(self.start_date),
			'endDate': self.get_time_string(self.end_date),
			'principal': self.principal,
			'pack': self.campaign_type
		}

	def reset_month(self, principal=None):
		self._settle_payments()
		self.start_date = timezone.now()
		self.active_day_end = None
		self.campaign = None
		self.principal = principal
		self.save()
	
	def reset_day(self):
		self._settle_payments()
		self.active_day_end = None
		self.campaign = None
		self.save()	
	
	def get_withdrawal_day(self):
		self._set_end_date()
		withdrawal_datetime = self.end_date - timedelta(1)
		return withdrawal_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

	def _settle_payments(self):
		active_days = self.active_days
		for day, paid_for in active_days.items():
			if not paid_for:
				self._settle_day(day)

	
	def _settle_day(self, day):
		try:
			Transaction.objects.create(
				type=Transaction.CREDIT,
				user=self.publisher.user,
				status=Transaction.SUCCESSFUL,
				comment="Payment for ads shared for campaign on {}".format(day),
				dollar_amount=self.get_day_pay()
			)
		except Exception as e:
			Logger.critical(str(e))
		else:
			self.active_days[day] = True


	def get_day_pay(self):
		subscription = self.get_plan()
		daily_growth_percent = subscription.daily_growth_percent
		profit = int( (daily_growth_percent / 100) * self.principal )
		return profit + principal


	def activate_day(self):
		self.reset_day()
		today = timezone.now()
		first_hour_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
		last_hour_of_day = today.replace(hour=23, minute=59, second=59, microsecond=0)
		self.active_day_end = last_hour_of_day
		self.active_days[str(first_hour_of_day)] = False


	def get_plan(self):
		principal = self.principal
		for plan, subscription in self.__class__.AVAILABLE_PLANS.items():
			if subscription.min <= principal <= subscription.max:
				return subscription

	def is_active_today(self):	
		if not self.active_day_end or not self.is_active():
			return False
		today = timezone.now()	
		last_hour_of_day = today.replace(hour=23, minute=59, second=59, microsecond=0)
		return last_hour_of_day == 	self.active_day_end			

	def is_active(self):
		if self.start_date and self.end_date:
			return timezone.now() < self.end_date
		return False
	
	def _set_end_date(self):
		self.start_date = self.start_date if self.start_date else timezone.now()		
		if self.start_date and not self.end_date:
			days = self.__class__.SUBSCRIPTION_DAYS
			self.end_date = self.start_date + timedelta(days=days)

	def save(self, *args, **kwargs):
		self._set_end_date()
		super().save(*args, **kwargs)