from django.dispatch import Signal, receiver

CampaignSubscribed = Signal(providing_args=["subscription"])
CampaignSubscriptionRenewed = Signal(providing_args=["subscription"])
PromoSubscribed = Signal(providing_args=['subscription'])
ExclusiveSubscribed = Signal(providing_args=['business'])


from AccountsApp.signals import signed_up
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from .models import CampaignSub, Transaction, Campaign, Promotion, Notification
from django.db.models.signals import pre_save, post_save
from .services import (
	CampaignService, BusinessService, PublisherService, TaskGenService, TaskCheckService, TransactionService
)
from django.utils import timezone
from threading import Thread
from . import tasks

User = get_user_model()

@receiver(ExclusiveSubscribed)
def handle_exclusive_sub(sender, **kwargs):
	business = kwargs['business']
	business_service = BusinessService()
	Thread(target=business_service.exclusive_subscribed, args=[business]).start()

@receiver(pre_save, sender=Campaign)
def campaign_approved(sender, **kwargs):
	campaign = kwargs['instance']
	if not campaign.is_approved:
		return
	del campaign.is_approved
	if not campaign.is_approved:
		business_service = BusinessService()
		Thread(target=business_service.compensate_business_referees, args=[campaign]).start()

@receiver(pre_save, sender=Campaign)
def campaign_declined(sender, **kwargs):
	campaign = kwargs['instance']
	if campaign.is_approved:
		return
	if campaign.is_approved ==  False:
		del campaign.is_approved
		if campaign.is_approved == None:
			campaign_service = CampaignService()
			Thread(target=campaign_service.campaign_declined, args=campaign).start()

@receiver(post_save, sender=Notification)
def mailable_notification_created(sender, **kwargs):
	if not kwargs['created']:
		return
	notification = kwargs['instance']
	
@receiver(pre_save, sender=Transaction)
def handle_successful_credit(sender, **kwargs):
	transaction = kwargs['instance']
	if  ( (transaction.type != Transaction.WITHDRAWAL) or 
				 (transaction.status != Transaction.SUCCESSFUL) ):
		return
	status = transaction.status
	del transaction.status
	if transaction.status == Transaction.SUCCESSFUL:
		pass # successful transaction

@receiver(pre_save, sender=Transaction)	
def deposit_handler(sender, **kwargs):
	transaction = kwargs['instance']
	if ( (transaction.type != Transaction.DEPOSIT) or
			 (transaction.status != Transaction.SUCCESSFUL)):
		return
	status = transaction.status
	del transaction.status
	if transaction.status != Transaction.SUCCESSFUL:
		return
	transaction_service = TransactionService()
	transaction_service.deposit_confirmed(transaction)

@receiver(CampaignSubscribed)
def campaign_subscription_handler(sender, **kwargs):
	subscription: CampaignSub = kwargs['subscription']
	tasks.campaign_subscribed.delay(subscription)

@receiver(PromoSubscribed)
def promo_subscription_handler(sender, **kwargs):
	subscription = kwargs['subscription']
	publisher_service = PublisherService()
	Thread(publisher_service.compensate_promoter_referees, args=[subscription] ).start()

@receiver(signed_up)
def sign_up_handler(sender, **kwargs):
	user: User = kwargs['user']
	request: HttpRequest = kwargs['request']
	referral_id = request.GET.get('ref', None)
	if not referral_id:
		return
	try:
		user.referee = User.objects.get(referral_id=referral_id)
		user.save()
	except User.DoesNotExist:
		return

