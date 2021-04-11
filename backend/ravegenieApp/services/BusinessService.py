from .TransactionService import TransactionService
from django.conf import settings
from ..signals import ExclusiveSubscribed

class BusinessService:
	def __init__(self):
		self.transaction_service = TransactionService()

	def subscribe_to_exclusive(self, business):
		principal = settings.EXCLUSIVE_COST
		business.reset_exclusive()
		self.transaction_service.transact_subscription(business, principal, 'Debit for exclusive subscription')
		business.start_subscription()
		business.save()
		ExclusiveSubscribed.send(sender=BusinessService, business=business)


	def exclusive_subscribed(self, business):
		referee = business.user.referee
		if not referee: 
			return
		referee_business = referee.business
		if referee_business.is_exclusive():
			bonus_amount = self.transaction_service.get_bonus_discounted_amount(
				settings.EXCLUSIVE_REF_BONUS, 
				settings.EXCLUSIVE_COST
			)
		else:
			bonus_amount = self.transaction_service.get_bonus_discounted_amount(
				settings.BUSINESS_REF_BONUS, 
				settings.EXCLUSIVE_COST
			)
		self.transaction_service.create_bonus(referee_business, bonus_amount, 'referral payment for exclusive referral')
	
	def compensate_business_referees(self, campaign):
		business = campaign.business
		referee = business.user.referee
		if not referee: 
			return
		referee_business = referee.business
		if not business.first_campaign_ref_paid:
			return self._compensate_regular_referees(campaign, referee_business, business)
			
		if referee_business.is_exclusive():
			return self._compensate_exclusive_referees(campaign, referee_business, business)
		
	
	def _compensate_regular_referees(self, campaign, referee_business, business):
		bonus_amount = self.transaction_service.get_bonus_discounted_amount(
			settings.BUSINESS_REF_BONUS, 
			campaign.cost
		)
		self.transaction_service.create_bonus(referee_business, bonus_amount, 'referral ad')
		business.first_campaign_ref_paid = True
		business.save()

	def _compensate_exclusive_referees(self, campaign, referee_business, business):
		bonus_amount = self.transaction_service.get_bonus_discounted_amount(
			settings.BUSINESS_REF_BONUS, 
			campaign.cost
		)
		self.transaction_service.create_bonus(referee_business, bonus_amount, 'referral ad')