from django.db import models
from utils.models import ModelMixin
from .business import Business
from django.utils import timezone
from datetime import timedelta
class Campaign(models.Model, ModelMixin):

	CAMPAIGN_DAYS = 30

	FACEBOOK = "FB"
	INSTAGRAM = "IG"
	TWITTER = "TW"

	CAMPAIGN_TYPES = (
		(FACEBOOK, "Facebook"),
		(INSTAGRAM, "Instagram"),
		(TWITTER, "Twitter")
	)
	
	start_date = models.DateTimeField(null=True)
	end_date = models.DateTimeField(null=True)
	raw_ad = models.TextField(max_length=50)
	ad_image = models.ImageField(upload_to='campaigns/', null=True)
	short_url = models.URLField(null=True)
	business = models.ForeignKey(Business, related_name='campaigns', null=True, on_delete=models.SET_NULL)
	is_approved = models.BooleanField(null=True)
	current_reach = models.PositiveIntegerField(default=0)
	required_reach = models.PositiveIntegerField(null=True)
	campaign_type = models.CharField(max_length=2, choices=CAMPAIGN_TYPES, db_index=True)
	created_at = models.DateTimeField(auto_now_add=True)
	internal = models.BooleanField(default=False)
	cost = models.DecimalField(decimal_places=2, max_digits=10)
 
	class Meta:
		ordering = ['-created_at']
	def get_dict(self):
		return {
			'approved': self.is_approved,
			'startDate': self.get_time_string(self.start_date),
			'endDate': self.get_time_string(self.end_date),
			'platform': self.campaign_type,
			'cost': self.cost,
			'ad': self.raw_ad,
			'adImage': self.ad_image,
		}

	def _set_end_date(self):
		if self.is_approved and not self.start_date:
			self.start_date = timezone.now()	
		if self.start_date and not self.end_date:
			days = self.__class__.CAMPAIGN_DAYS
			self.end_date = self.start_date + timedelta(days=days)

	def save(self, *args, **kwargs):
		self._set_end_date()
		super().save(*args, **kwargs)
	
	def is_expired(self):
		if not self.end_date:
			return True
		return self.end_date <= timezone.now()