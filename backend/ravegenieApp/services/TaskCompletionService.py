from ..models import Task, CampaignSub
from .TransactionService import TransactionService
import json
import logging

Logger = logging.getLogger('ravegenieApp')


class TaskCompletionService:
	
	def __init__(self):
		self.manual_tasks = (Task.FIRST_SUB_IN_SUB, Task.FIRST_SUB_TO_ALL)	
		self.bonus_service = TransactionService()

	def complete_task(self, task):
		if task.type in self.manual_tasks:
			return self._complete_manual_tasks(task)
		task_def = task.get_def()
		if task.required_point <= task.present_point and not task.done:
			status = self.bonus_service.create_bonus(
				publisher=task.publisher, 
				amount=task_def.compensation,
				comment=task.description,
			)
			if status:
				task.done = True
				task.save()
	
	def _complete_manual_tasks(self, task):
		self._complete_first_sub_to_all(task)
		self._complete_first_sub_within_sub(task)	

	def _complete_first_sub_within_sub(self, task):
		if 	task.type != Task.FIRST_SUB_IN_SUB:
			return
		task_def = task.get_def()
		if task.required_point <= task.present_point and not task.done:
			comment = json.loads(task.comments)
			sub_id = comment.get('subscription_id', None)
			if not sub_id:
				return	
			try:
				subscription = CampaignSub.objects.get(id=int(sub_id))
			except CampaignSub.DoesNotExist as e:
				Logger.error(str(e))
			else:
				amount = self._get_discount(subscription.principal, task_def.compensation)
				status = self.bonus_service.create_bonus(
					publisher=task.publisher, 
					amount=amount,
					comment=task.description,
				)
				if status:
					task.done = True
					task.save()
	
	def _complete_first_sub_to_all(self, task):
		if 	task.type != Task.FIRST_SUB_IN_SUB:
			return
		task_def = task.get_def()
		if task.required_point <= task.present_point and not task.done:
			comment = json.loads(task.comments)
			sub_ids = comment.get('others', None)
			if not sub_ids or len(sub_ids) < 3:
				return
			int_sub_ids = [int(id) for id in sub_ids]
			subscriptions = CampaignSub.objects.filter(id__in=int_sub_ids)[:3]
			principal = sum([sub.principal for sub in subscriptions])
			if not principal:
				return	
			amount = self._get_discount(principal, task_def.compensation)
			status = self.bonus_service.create_bonus(
				publisher=task.publisher, 
				amount=amount,
				comment=task.description,
			)
			if status:
				task.done = True
				task.save()
	
	def _get_discount(self, amount, percent):
		return (percent / 100) * amount

