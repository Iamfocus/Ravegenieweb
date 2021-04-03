from django.db import models
from utils.models import ModelMixin
from .promotion_spec import PromotionSpec
from .business import Business
from django.utils import timezone
from datetime import timedelta

class Promotion(models.Model, ModelMixin):
	
	PROMOTION_DAYS = 30

	is_approved = models.BooleanField(null=True)
	raw_ad = models.TextField(max_length=100)
	start_date = models.DateTimeField(null=True)
	end_date = models.DateTimeField(null=True)
	required_reach = models.PositiveIntegerField(null=True)
	current_reach = models.IntegerField(default=0)
	promotion_spec = models.ForeignKey(PromotionSpec, on_delete=models.SET_NULL, null=True)
	business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, related_name='promotions')
	created_at = models.DateTimeField(auto_now_add=True)
	internal = models.BooleanField(default=False)
	
	class Meta:
		ordering = ['-created_at']
		
	def get_dict(self):
		return {
			'approved': self.is_approved,
			'ad': self.raw_ad,
			'startDate': self.get_time_string(self.start_date),
			'endDate': self.get_time_string(self.end_date),
			'expectedReach': self.expected_reach,
			'currentReach': self.current_reach,
			'promotionSpec': self.promotion_spec.get_dict(),
			'business': str(self.business.user),
			'createdAt': self.get_time_string(self.created_at),
			'internal': self.internal,
			'expired': self.is_expired()
		}
	
	def _set_end_date(self):
		if self.is_active and not self.start_date:
			self.start_date = timezone.now()			
		if self.start_date and not self.end_date:
			days = self.__class__.PROMOTION_DAYS
			self.end_date = self.start_date + timedelta(days=days)

	def save(self, *args, **kwargs):
		self._set_end_date()
		super().save(*args, **kwargs)
	
	def is_expired(self):
		return self.end_date <= timezone.now()
		