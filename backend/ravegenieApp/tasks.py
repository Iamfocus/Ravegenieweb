from ravegenie import celery_app as app
from .services import (
	PublisherService, 
	TaskCheckService, 
	TaskGenService, 
	TaskSupervisorService, 
	PromotionSupervisorService,
	CampaignsupervisorService
)
from django.utils import timezone
from .models import CampaignSub

@app.task
def supervise_tasks():
	supervisor = TaskSupervisorService()
	supervisor.clean()

@app.task
def complete_promotion_actions():
	supervisor = PromotionSupervisorService()
	supervisor.settle_promotion_actions()

@app.task
def supervise_campaigns():
	supervisor = CampaignsupervisorService()
	supervisor.clean()

@app.task
def send_mails():
	pass

@app.task(max_retries=2)
def campaign_subscribed(subscription_id):
	subscription = CampaignSub.objects.get(id=subscription_id)
	publisher_service = PublisherService()
	publisher_service.compensate_publisher_referees(subscription)
	task_generator = TaskGenService()
	task_generator.generate_tasks(timezone.now(), subscription)
	task_checker = TaskCheckService()
	task_checker.check()