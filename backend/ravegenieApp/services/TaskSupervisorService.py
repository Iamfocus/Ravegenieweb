from .TaskCompletionService import TaskCompletionService
from ..models import Task
from django.db.models import Q
from django.utils import timezone
import logging

Logger = logging.getLogger('raveGenieApp')

class TaskSupervisorService:
	
	def clean(self):
		self._complete_tasks()
		self._delete_expired_tasks()

	def _complete_tasks(self):
		query = Q(done=False) and Q(end_date__gte=timezone.now())
		tasks = Task.objects.filter()
		completer = TaskCompletionService()
		for task in tasks:
			try:
				completer.complete_task(task)
			except Exception as e:
				Logger.error(str(e))
			
	def _delete_expired_tasks(self):
		Task.objects.filter(end_date__lt=timezone.now()).delete()
