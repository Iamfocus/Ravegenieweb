from django.db import models
from utils.models import ModelMixin
from django.utils import timezone
from datetime import timedelta
import time

class Business(models.Model, ModelMixin):

	SUBSCRIPTION_DAYS = 30

	exclusive_start_date = models.DateTimeField(null=True)
	exclusive_end_date = models.DateTimeField(null=True)
	account_balance = models.DecimalField(default=0, decimal_places=2, max_digits=10)
	bonus_balance = models.DecimalField(default=0, decimal_places=2, max_digits=10)
	business_details = models.TextField(null=True, max_length=500)
	first_campaign_ref_paid = models.BooleanField(default=False)
	exclusive_spots_used = models.PositiveSmallIntegerField(default=0)
	class Meta:
		ordering = ['-id']
		models.CheckConstraint(check=models.Q(account_balance__gt=0), name='ensure_balance_is_gt_zero')
		models.CheckConstraint(check=models.Q(bonus_balance__gt=0), name='ensure_bonus_is_gt_zero')
	
	def reset_exclusive(self):
		self.exclusive_end_date = None
		self.exclusive_start_date = None
		self.exclusive_spots_used = 0
		
	def is_exclusive(self):
		if self.exclusive_end_date:
			return timezone.now() < self.exclusive_end_date
		return False

	def start_subscription(self):
		self.exclusive_start_date = timezone.now()
	
	def end_subscription(self):
		self.exclusive_start_date = None
		self.exclusive_end_date = None

	def _set_exclusive_end(self):
		if self.exclusive_start_date and not self.exclusive_end_date:
			days = self.__class__.SUBSCRIPTION_DAYS
			self.exclusive_end_date = self.exclusive_start_date + timedelta(days=days)

	def save(self, *args, **kwargs):
		self._set_exclusive_end()
		super().save(*args, **kwargs)			
		
	def get_dict(self):
		business_data =  {
			"exclusiveStartDate": self.get_time_string(self.exclusive_start_date),
			"exclusiveEndDate": self.get_time_string(self.exclusive_end_date),
			'isExclusive': self.is_exclusive(),
			'accountBalance': self.account_balance,
			'bonusBalance': self.bonus_balance,
		}
		user_data = self.user.get_dict()
		user_data.update(business_data)
		return user_data