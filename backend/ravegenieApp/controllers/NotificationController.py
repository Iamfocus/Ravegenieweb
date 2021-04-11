from utils.controller import Controller
from utils.shortcuts import json_response
from .. import forms
from ..models import Notification
from rest_framework.decorators import api_view

class NotificationController(Controller):


	@Controller.route()
	@Controller.decorate(api_view(['POST']))
	def create(self, request):
		form = forms.CreateNotification(request.data)
		self.validate_form(form)
		data = form.cleaned_data
		notification = Notification.object.create(
			subject=data['subject'],
			body=data['body']
		)
		notification.recipients.set(data['recipients'])
		return json_response(status=True)
	
	@Controller.route('read/<int:id>')
	def read(self, request, id):
		user = request.user
		notification = Notification.objects.get(id=id)
		user.notifications.remove(notification)
		return json_response(True)

		