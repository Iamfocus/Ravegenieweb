from django.db import transaction
import logging
from .TransactionService import TransactionService
from ..models import PromoSubscriptions, Promotion, PromotionAction
from ..signals import PromoSubscribed
from django.db.models import Q
from ..exceptions import PromotionError
from django.utils import timezone
from django.db.models import F


Logger = logging.getLogger('ravegenieApp')
class PromotionService:

	def __init__(self):
		self.transaction_service = TransactionService()

	def create_promotion(self, business, cost, link, end_date, promotion_spec):
		self.transaction_service.transact_subscription(business, cost)
		promotion = Promotion.objects.create(
			start_date=timezone.now(),
			end_date=end_date,
			raw_ad=link,
			promotion_spec=promotion_spec,
			business=business,
		)
		return promotion


	def subscribe(self, publisher, package):
		plan = PromoSubscriptions.PLANS[package]
		principal = plan.price
		with transaction.atomic():	
			self.transaction_service.transact_subscription(publisher, principal)
			subscription = PromoSubscriptions.objects.create(publisher=publisher, type=package)
			PromoSubscribed.send(sender=self.__class__, subscription=subscription)
			return subscription
	

	def get_promotions(self, publisher):
		if not publisher.first_promotion_executed:
			publisher.first_promotion_executed = True
			publisher.save()
			query = (Q(is_approved=True) and Q(internal=True) and 
							Q(end_date__gt=timezone.now()) )
			return Promotion.objects.filter(query)
		query =  Q(is_approved=True) and Q(internal=False) and Q(end_date__gt=timezone.now())
		return Promotion.objects.filter(query)
	
	def start_promotion(self, publisher, promotion_id):
		if not publisher.has_promo_sub():
			raise PromotionError('You have no subscription')
		if len(publisher.promo_actions.all()) >= PromoSubscriptions.PROMOS_PER_DAY:
			raise PromotionError('daily promo limit reached')
		promotion = Promotion.objects.get(id=promotion_id)
		if promotion.is_expired():
			raise PromotionError('This promotion is expired please pic another')
		promotion.current_reach = F('current_reach') + 1
		promotion.save()
		PromotionAction.objects.create(
			publisher=publisher,
			promotion=promotion
		)



	