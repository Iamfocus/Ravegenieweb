from ..models import Task, CampaignSub, Campaign
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import json

class TaskCheckService:
	def __init__(self, subscription):
		self.publisher = subscription.publisher
		parent = self.publisher.user.referee
		self.parent_publisher = parent.publisher
		self.publisher_tasks = self.get_tasks(self.publisher)
		self.parent_tasks = self.get_tasks(self.parent_publisher)
		self.subscription = subscription

	def check(self): 
		self.check_first_referral_task()
		self.check_referral_on_sub_day() 
		self.check_referral_on_withdraw_day()
		self.check_refs_this_month()
		self.check_three_friends_two_refs()
		self.check_first_sub_within_sub()
		self.check_first_sub_to_all()

	def check_first_referral_task(self):
		task_type = Task.FIRST_REF
		task = self.parent_tasks.get(task_type, None)
		if not task:
			return
		if (not self.publisher.first_referral_paid and 
			not self.parent_publisher.first_referral_received):
			self.publisher.first_referral_paid = True
			self.parent_publisher.first_referral_receive = True
			self.publisher.save()
			self.parent_publisher.save()
			task.present_point = task.required_point
			task.save()
	
	def check_referral_on_sub_day(self):
		task_type = Task.REF_ON_SUB_DAY
		task = self.parent_tasks.get(task_type, None)
		if not task:
			return
		if not self.subcribed_today(self.parent_publisher):
			return
		task.present_point = task.required_point
		task.save()
	
	def check_referral_on_withdraw_day(self):
		task_type = Task.REF_ON_WDRW_DAY
		task = self.parent_tasks.get(task_type, None)
		if not task:
			return
		if not self.is_withdrawal_day(self.parent_publisher):
			return
		task.present_point = task.required_point	
		task.save()
	
	def check_refs_this_month(self):
		task_types =  [Task.REF_3_MNT, Task.REF_10_MNT, Task.REF_20_MNT]
		tasks = [self.parent_tasks.get(task_type, None) for task_type in task_types  
												if self.parent_tasks.get(task_type, None)]
		if not tasks:
			return
		if not self.parent_publisher.has_active_campaign_subs():
			return 
		for task in tasks:
			task.present_point += 1
			task.save()
	
	def check_three_friends_two_refs(self):
		task_type = Task.REF_3_FR_2_REF
		try:
			grand_parent = self.parent_publisher.user.publisher
			query = Q(publisher=grand_parent) and Q(end_date__gt=timezone.now()) and Q(type=task_type)	
			grand_parent_task = Task.objects.get(query)
		except Exception:
			return
		try:
			parents_fulfilled = json.loads(grand_parent_task.comments)
		except json.JSONDecodeError:
			parents_fulfilled = {}
		parent_count = int(parents_fulfilled.get(str(self.parent_publisher.pk), 0))
		if parent_count >= 2:
			counter = 0
			for parent, count in parents_fulfilled.items():
				count = int(count)
				if count >= 2:
					counter += 1
			grand_parent_task.present_point = counter	
			return
			parent_count += 1
			parents_fulfilled[str(self.parent_publisher.pk)] = parent_count
			comments = json.dumps(parents_fulfilled)
			grand_parent_task.comments = comments
			grand_parent_task.save()
	
	def check_first_sub_within_sub(self):
		self._check_first_multi_sub(2, Task.FIRST_SUB_IN_SUB)
	
	def check_first_sub_to_all(self):
		self._check_first_multi_sub(len(Campaign.CAMPAIGN_TYPES), Task.FIRST_SUB_TO_ALL)

	def _check_first_multi_sub(self, no_of_subs, task_type):
		task = self.publisher_tasks.get(task_type, None)
		if not task:
			return
		subscriptions = self.publisher.campaign_subs.all()
		if len(subscriptions) < no_of_subs:
			return
		valid = 0
		for subscription in subscriptions:
			if ( subscription.is_active() and 
				subscription.principal > CampaignSub.MINIMUM_SUB ):
				valid += 1
		task.required_point = valid
		task.comment = json.dumps({'subscription_id': str(self.subscription.pk), 
										'others': [str(sub.pk) for sub in subscriptions]})
		task.save()
		

	def subscribed_today(self, publisher):
		today = timezone.today()
		for sub in publisher.campaign_subs.all():
			if today - sub.start_date < timedelta(hours=24):
				return True
		return False
	
	def is_withdrawal_day(self, publisher):
		today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
		return today in publisher.get_withdrawal_days()

	def get_tasks(self, publisher):
		query = Q(publisher=publisher) and Q(end_date__gt=timezone.now())	
		raw_tasks = Task.objects.filter(query)
		return {task.type: task for task in raw_tasks}