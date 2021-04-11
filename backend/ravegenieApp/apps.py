from django.apps import AppConfig


class RavegenieappConfig(AppConfig):
	name = 'ravegenieApp'
	
	def ready(self):
		from . import signals
