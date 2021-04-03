from django.db import models
from utils.models import ModelMixin
from .user import User

class Feedback(models.Model, ModelMixin):
	
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='feedbacks')
	comment = models.CharField(max_length=100)
	rating = models.PositiveIntegerField(default=5)
	approved = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering = ['-created_at']
		
	def get_dict(self):
		return {
			'user': str(self.user),
			'comment': self.comment,
			'approved': self.approved,
			'createdAt': self.get_time_string(self.created_at)
		}