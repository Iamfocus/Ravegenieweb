from ..models import Transaction, CampaignSub, Campaign
from django.db import transaction, IntegrityError
from django.db.models import Q
from ..exceptions import TransactionError, CampaignError
import logging
from django.conf import settings
from ..signals import CampaignSubscribed, CampaignSubscriptionRenewed
from .TransactionService import TransactionService
from django.utils import timezone

Logger = logging.getLogger("ravegenieApp")

class CampaignService:
	
	def __init__(self):
		self.transaction_service = TransactionService()

	def create_subscription(self, publisher, data):
		principal = data['principal']
		with transaction.atomic():	
			self.transaction_service.transact_subscription(publisher, principal)
			subscription = CampaignSub.objects.create(
				principal=data['principal'], campaign_type=data['type'], publisher=publisher)
			print('befre signals')
			CampaignSubscribed.send(sender=self.__class__, subscription=subscription)
			return subscription

	def create_campaign(self, business, end_date, cost, ad_image, ad, campaign_type):
		if business.is_exclusive() and business.exclusive_spots_used < settings.CAMPAIGNS_PER_EXCLUSIVE_SUB:
			business.exclusive_spots_used += 1
		else:
			self.transaction_service.transact_subscription(business, cost)
		campaign = Campaign.objects.create(
			start_date=timezone.now(),
			end_date=end_date,
			cost=cost,
			ad_image=ad_image,
			business=business,
			raw_ad=ad,
			campaign_type=campaign_type
		)
		return campaign

	def renew_subscription(self, publisher, sub_id):
		subscription = CampaignSub.objects.get(id=sub_id)
		principal = self._get_renew_discounted_principal(subscription.principal)
		if subscription.publisher != publisher:
			Logger.error("Fraudulent renewal by {}".format(str(publisher.user)))			
			raise TransactionError("Fraudulent transaction attempted")
		with transaction.atomic():
			self.transaction_service.transact_subscription(publisher, principal, "campaign subscription renewal")
			subscription.reset_month(principal)
			subscription.refresh_from_db()
			CampaignSubscriptionRenewed.send(sender=self.__class__, subscription=subscription)
			return subscription

	def start_campaign(self, publisher, subscription_id, campaign_id):
		subscription = CampaignSub.objects.get(id=subscription_id)
		campaign = Campaign.objects.get(id=campaign_id)	
		if (subscription.publisher != publisher or 
						campaign.campaign_type != subscription.campaign_type or campaign.is_expired()):
			Logger.error("suspicious campaign by %s", str(publisher.user))
			raise CampaignError("suspicious operation")		
		if subscription.is_active_today():
			raise CampaignError("campaign already running for the day")
		subscription.activate_day()
		subscription.campaign = campaign
		subscription.save()
		campaign.active_days += 1
		campaign.save()
	
	def campaign_declined(self, campaign):
		business = campaign.business
		self.transaction_service.credit(business, campaign.cost, 'Cost of Declined transaction refunded')
		campaign.delete()
	
	def get_publisher_campaigns(self, campaign_type, publisher):
		if not publisher.first_ad_executed:
			publisher.first_ad_executed = True
			publisher.save()
			query = Q(campaign_type=campaign_type) and Q(internal=True) and Q(end_date__gt=timezone.now())
			return Campaign.objects.filter()
		query = ( Q(campaign_type=campaign_type) and Q(is_approved=True) and
								 Q(internal=False) and Q(end_date__gt=timezone.now()) )
		return Campaign.objects.filter(query)


	def _get_renew_discounted_principal(self, principal):
		discount_percent = settings.CAMPAIGN_RENEW_DISCOUNT_PERCENT
		discount = ( discount_percent / 100 ) * principal
		return principal - discount
	
	

	