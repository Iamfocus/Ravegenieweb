from ..models import Publisher, PromoSubscriptions
from .TransactionService import TransactionService
from django.conf import settings

class PublisherService:
	def __init__(self):
		self.transaction_service = TransactionService()
	
	def compensate_publisher_referees(self, subscription):
		publisher = subscription.publisher
		if publisher.first_referral_paid:
			return
		referee_publisher = publisher.get_referee
		if not referee_publisher:
			return
		bonus_amount = self.transaction_service.get_bonus_discounted_amount(
			settings.PUBLISHER_REF_BONUS, 
			subscription.principal
		)
		publisher_name = str(publisher.user)
		self.transaction_service.create_bonus(
			referee_publisher, bonus_amount, 
			f'referral bonus for user {publisher_name}'
		)
	
	def compensate_promoter_referees(self, subscription):
		compensation = PromoSubscriptions.COMPENSATION
		promoter = subscription.publisher
		principal = subscription.get_plan().referral_price
		for generation, data in compensation.items():
			promoter = promoter.user.referee
			percentage = data[subscription.type]
			self.compensate_promoter(promoter, percentage, principal)	

	def compensate_promoter(self, promoter, percentage, principal):
		bonus_amount = self.transaction_service.get_bonus_discounted_amount(
			percentage,
			principal
		)
		self.transaction_service.create_bonus(
			promoter, 
			bonus_amount, 
			'referral bonus for user'
		)
