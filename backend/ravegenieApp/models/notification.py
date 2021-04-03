from django.db import models
from utils.models import ModelMixin
from .user import User

class Notification(models.Model, ModelMixin):
	subject = models.CharField(max_length=30)
	body = models.CharField(max_length=100)
	mail = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	recipients = models.ManyToManyField(User, related_name='notifications')

	class Meta:
		ordering = ['-created_at']
	def get_dict(self):
		return {
			'subject': self.subject,
			'body': self.body,
			'read': self.read,
		}