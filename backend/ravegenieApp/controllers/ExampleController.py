from utils.controller import Controller
from utils.shortcuts import json_response
from rest_framework.decorators import api_view, authentication_classes
from utils.decorators import ensure_signed_in
from django.views.decorators.csrf import csrf_exempt
from ..models import Publisher, CampaignSub
from django.core.exceptions import ObjectDoesNotExist


class ExampleController(Controller):

	def __ini__(self):
		self.mad = "ness"
	
	@Controller.route("create/<str:id>")
	@Controller.decorate(api_view(["POST"]), ensure_signed_in)
	def create(self, request, id):
		
		return json_response(status=True, data=self.mad)

