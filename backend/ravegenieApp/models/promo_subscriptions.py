from django.db import models
from utils.models import DictionaryField, ModelMixin
from .publisher import Publisher
from .promotion import  Promotion
from .transaction import  Transaction
from django.utils import timezone
import logging
from datetime import timedelta
import collections
from django.conf import settings

Logger = logging.getLogger('ravegenie')

class PromoSubscriptions(models.Model, ModelMixin):
	

	ELITE = 'ELT'
	BASIC = 'BSC'
	BASIC_PRICE = settings.TO_DOLLAR(565)
	ELITE_PRICE = settings.TO_DOLLAR(2587)

	PROMOS_PER_DAY = 3
	
	PLAN = collections.namedtuple('PLAN', ['days', 'price', 'referral_price'])
	PLANS = {
		BASIC: PLAN(30, BASIC_PRICE, settings.TO_DOLLAR(500)),
		ELITE: PLAN(365, ELITE_PRICE, settings.TO_DOLLAR(2500)),
		BASIC_PRICE: PLAN(30, BASIC_PRICE, settings.TO_DOLLAR(500)),
		ELITE_PRICE: PLAN(365, ELITE_PRICE, settings.TO_DOLLAR(2500))
	}
	PACKAGES = (
		(ELITE, "elite"),
		(BASIC, "basic")
	)
	PRICES = (
		(ELITE_PRICE, "elite"),
		(BASIC_PRICE, "basic")
	)
	COMPENSATION = {
			1 : {BASIC: 20, ELITE: 30},
			2 : {BASIC: 5, ELITE: 10},
			3 : {BASIC: 3, ELITE: 5},
			4 : {BASIC: 2, ELITE: 3},
			5 : {BASIC: 1, ELITE: 2},
	}

	start_date = models.DateTimeField(auto_now_add=True)
	end_date = models.DateTimeField()
	publisher = models.OneToOneField(Publisher, on_delete=models.CASCADE, related_name='promo_sub')
	type = models.CharField(max_length=3, choices=PACKAGES)

	class Meta:
		ordering = ['-start_date']
		
	def get_dict(self):
		return {
			'isActive': self.is_active(),
			'plan': self.type, 
			'startDate': self.get_time_string(self.start_date),
			'endDate': self.get_time_string(self.end_date)
		}

	def reset(self):
		self.start_date = timezone.now()
				

	def is_active(self):
		if self.start_date and self.end_date:
			return timezone.now() < self.end_date
		return False
	
	def _set_end_date(self):
		self.start_date = self.start_date if self.start_date else timezone.now()
		if self.start_date and not self.end_date:
			days = self.get_plan().days
			self.end_date = self.start_date + timedelta(days=days)

	def save(self, *args, **kwargs):
		self._set_end_date()
		super().save(*args, **kwargs)
	
	def get_plan(self):
		return self.__class__.PLANS[self.type]