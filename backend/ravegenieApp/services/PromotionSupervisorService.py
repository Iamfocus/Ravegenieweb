from ..models import PromoSubscriptions, Promotion, PromotionAction, Transaction
from django.db.models import Q
from django.utils import timezone
from .TransactionService import TransactionService
from datetime import timedelta
from .MiscService import yesterday

class PromotionSupervisorService:
	def __init__(self):
		self._transaction_service = TransactionService()
	
	def clean(self):
		self.settle_promotion_actions()
		self._delete_expired_promotion_actions()
		self._delete_expired_promotions()
		self._delete_expired_subscriptions()
	

	def settle_promotion_actions(self):
		query = Q(done=False) and Q(end_date__lte=timezone.now())
		actions = PromotionAction.objects.filter(query)
		for action in actions:
			if self._confirm_action(action):
				status = self._compensate_promoter(action)
				action.done  = status
				action.save()
	
	def _delete_expired_promotion_actions(self):
		query = Q(done=True) or Q(end_date__lte=timezone.now())
		PromotionAction.objects.filter(query).delete()
	
	def _delete_expired_subscriptions(self):
		PromoSubscriptions.objects.filter(end_date__lte=yesterday()).delete()
	
	def _delete_expired_promotions(self):
		query = Q(internal=False) and Q(end_date__lte=yesterday())
		PromoSubscriptions.objects.filter(query).delete()

	def _compensate_promoter(self, action):
		spec = action.promotion.promotion_spec
		amount = spec.publisher_unit_compensation
		publisher = action.publisher
		self._transaction_service.credit(publisher, amount, 'Promotion credit')


	def _confirm_action(self, action):
		"""
		Todo.

		This method should take the promotion for an action and 
		confirm against facebook or Ig or twitter records to ensure that the 
		action was actually taken by the publisher.
		"""
		return True