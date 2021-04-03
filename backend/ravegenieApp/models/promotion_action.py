from django.db import models
from utils.models import ModelMixin
from .promotion import Promotion
from .publisher import Publisher
from django.utils import timezone
from datetime import timedelta

class PromotionAction(models.Model, ModelMixin):
	
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='promo_actions')
	promotion = models.ForeignKey(Promotion, on_delete=models.DO_NOTHING, related_name='actions')
	start_date = models.DateTimeField(auto_now_add=True)
	end_date = models.DateTimeField()
	done = models.BooleanField(default=False)

	class Meta:
		ordering = ['-start_date']

	def get_dict(self):
		return {
			'startDate': self.get_time_string(self.start_date),
			'endDate': self.get_time_string(self.end_date),
			'done': self.done
		}

	def _set_end_date(self):
		self.start_date = self.start_date if self.start_date else timezone.now()
		if self.start_date and not self.end_date:
			self.end_date = self.start_date + timedelta(hours=3)

	def save(self, *args, **kwargs):
		self._set_end_date()
		super().save(*args, **kwargs)
	
