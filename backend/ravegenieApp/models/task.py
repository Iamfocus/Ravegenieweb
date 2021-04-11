from django.db import models
from utils.models import ModelMixin
from .publisher import Publisher
import collections
from .campaign import Campaign
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

def convert_to_naira(dollar_amount):
	SDR = int(settings.SDR)
	return dollar_amount * SDR
class Task(models.Model, ModelMixin):
	
	FIRST_REF = "FR"
	REF_ON_SUB_DAY = "ROSD"
	REF_ON_WDRW_DAY = "ROWD"
	REF_3_MNT = "R3M"
	REF_10_MNT = "R10M"
	REF_20_MNT = "R20M"
	REF_3_FR_2_REF = "R3F2R"
	FIRST_SUB_IN_SUB = "FSINS"
	FIRST_SUB_TO_ALL = "FSTA"
	
	TASK_LIFE_TIME_DAYS = 30
	TASK_DEF = collections.namedtuple("TASK_DEF", ['desc', 'compensation', 'req_point'])
	AVAILABLE_TASKS = {
		FIRST_REF: TASK_DEF('Get your First referral', 1.5, 1),
		REF_ON_SUB_DAY: TASK_DEF('Refer a friend on the same day as subscription', 2, 1),
		REF_ON_WDRW_DAY: TASK_DEF('Refer two friends on the day of your withdrawal', 10, 2),
		REF_3_MNT: TASK_DEF('Refer 3 friends this month ', 4, 3),
		REF_10_MNT: TASK_DEF('Refer 10 friends this month', 25, 10),
		REF_20_MNT: TASK_DEF('Refer 20 friends this month', 40, 20),
		REF_3_FR_2_REF: TASK_DEF("""Refer 3 friends this month who each get 2 referrals 
								within the same subscriptionperiod""", 15, 3),
		FIRST_SUB_IN_SUB: TASK_DEF("""First personal subscription to a 
							different social pack within a subscription period""", 10, 2),
		FIRST_SUB_TO_ALL: TASK_DEF("""First personal subscription to all three 
				social packs within a subscription period""", 15, len(Campaign.CAMPAIGN_TYPES))
	}


	start_date = models.DateTimeField(null=True)
	end_date = models.DateTimeField(null=True)
	type = models.CharField(max_length=7)
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
	required_point = models.PositiveIntegerField(default=0)
	present_point = models.PositiveIntegerField(default=0) 
	description = models.TextField()
	done = models.BooleanField(default=False)
	comments =  models.TextField(default='')

	def get_dict(self):
		return {
			'startDate': self.get_time_string(self.start_date),
			'endDate': self.get_time_string(self.end_date),
			'type': self.type,
			'percentComplete': self._percent_complete(),
			'done': self.done,
			'description': self.description,
			'comment': self.comments
		}
	
	def _percent_complete(self):
		try:
			fraction = self.present_point / self.required_point
		except ZeroDivisionError:
			return 0
		else:
			return fraction * 100

	def _set_description(self):
		task_def = self.get_def()
		description = task_def.desc
		self.description = description		

	def _set_required_point(self):
		task_def = self.get_def()
		required_point = task_def.req_point	
		self.required_point = required_point
	
	def _set_end_date(self):
		self.start_date = self.start_date if self.start_date else timezone.now()
		if self.start_date and not self.end_date:
			days = self.__class__.TASK_LIFE_TIME_DAYS	
			self.end_date = self.start_date + timedelta(days=days)

	def save(self, *args, **kwargs):
		self._set_end_date()
		self._set_description()
		self._set_required_point()
		super().save(*args, **kwargs)

	def get_def(self):
		return self.__class__.AVAILABLE_TASKS[self.type]


