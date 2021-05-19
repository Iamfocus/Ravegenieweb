from ..models import Publisher, CampaignSub, Task
from django.utils import timezone
from datetime import timedelta, datetime
class TaskGenService:
	
	def __init__(self, start_date: datetime, subscription: CampaignSub):
		self.publisher = subscription.publisher
		self.start_date = start_date
		self.subscription = subscription

	def generate_tasks(self):
		if not self._publisher_is_eligible():
			return		
		self.gen_first_ref_task()
		self.gen_ref_on_sub_day_task()
		self.gen_ref_on_withdraw_day()
		self.gen_ref_three_monthly()
		self.gen_ref_ten_monthly()
		self.gen_ref_twenty_monthly()
		self.gen_ref_three_friends_two_ref()
		self.gen_first_sub_within_sub()
		self.gen_sub_to_all()

	def _publisher_is_eligible(self):
		return self.subscription.campaign_type != CampaignSub.MINIMUM_SUB

	def gen_first_ref_task(self):
		if not self.publisher.first_referral_recieved:
			Task.objects.create(
				start_date=self.start_date,
				type=Task.FIRST_REF,
				publisher=self.publisher,
			)
	
	def gen_ref_on_sub_day_task(self):
		task, created = Task.objects.get_or_create(
			type=Task.REF_ON_SUB_DAY,
			publisher=self.publisher,
			defaults={'start_date': self.start_date}
		)
		end_date = self.start_date + timedelta(1)
		task.end_date = end_date
		task.save()

	def gen_ref_on_withdraw_day(self):
		task, created = Task.objects.get_or_create(
			type=Task.REF_ON_WDRW_DAY,
			publisher=self.publisher,
			defaults={'start_date': self.start_date}
		)
		end_date = task.start_date + timedelta(29)
		task.end_date = end_date
		task.save()
	
	def gen_ref_three_monthly(self):
		self._gen_monthly_task(Task.REF_3_MNT)	

	def gen_ref_ten_monthly(self):
		self._gen_monthly_task(Task.REF_10_MNT)
	
	def gen_ref_twenty_monthly(self):
		self._gen_monthly_task(Task.REF_20_MNT)
	
	def gen_ref_three_friends_two_ref(self):
		self._gen_monthly_task(Task.REF_3_FR_2_REF)
	
	def gen_first_sub_within_sub(self):
		if not self.publisher.first_multi_sub:	
			self._gen_monthly_task(Task.FIRST_SUB_IN_SUB)
	
	def gen_sub_to_all(self):
		if not self.publisher.frist_all_sub:	
			self._gen_monthly_task(Task.FIRST_SUB_TO_ALL)

	def _gen_monthly_task(self, type_signature):
		task, created = Task.objects.get_or_create(
			type=type_signature,
			publisher=self.publisher,
			defaults={'start_date': self.start_date}
		)
		end_date = task.start_date + timedelta(30)
		task.end_date = end_date
		task.save()
	
		


