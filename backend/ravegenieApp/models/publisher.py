from django.db import models
from utils.models import ModelMixin
from django.core.exceptions import ObjectDoesNotExist
class Publisher(models.Model, ModelMixin):
	
	GUARDED = set(["account_balance", "bonus_account_balance"])

	bank_account_no = models.PositiveIntegerField(null=True)
	bank_name = models.CharField(max_length=25, null=True)
	coin_type = models.CharField(max_length=3, null=True)
	wallet_address = models.CharField(null=True, max_length=64)
	account_balance = models.DecimalField(default=0, decimal_places=2, max_digits=10)
	bonus_balance = models.DecimalField(default=0, decimal_places=2, max_digits=10)
	first_ad_executed = models.BooleanField(default=False)
	first_promotion_executed = models.BooleanField(default=False)
	first_referral_paid = models.BooleanField(default=False)
	first_referral_recieved = models.BooleanField(default=False)
	first_multi_sub = models.BooleanField(default=False)
	frist_all_sub = models.BooleanField(default=False)

	class Meta:
		models.CheckConstraint(check=models.Q(account_balance__gt=0), name='ensure_balance_is_gt_zero')
		models.CheckConstraint(check=models.Q(bonus_balance__gt=0), name='ensure_bonus_is_gt_zero')
		ordering = ['-id']

	def get_dict(self):
		publisher_data = {
			"bankAccountNumber": self.bank_account_no,
			"bankName": self.bank_name,
			"coinType": self.coin_type,
			"walletAddress": self.wallet_address,
			"accountBalance": self.account_balance,
			"bonusBalance": self.bonus_balance,
		}
		user_data = self.user.get_dict()
		user_data.update(publisher_data)
		return user_data		
	
	def is_bonus_redeemable(self):
		pass
	
	def get_withdrawal_days(self):
		days = []
		for campaign_sub in self.campaign_subs.all():
			if campaign_sub.is_active():
				days.append(campaign_sub.get_withdrawal_day())
		return days

	def has_active_campaign_sub(self):
		for campaign_sub in self.campaign_subs.all():
			if campaign_sub.is_active():
				return True
		return False
			
	def has_campaign_sub(self):
		return self.campaign_subs.exists()
	
	def has_campaign_of_type(self, campaign_type):
		for sub in self.campaign_subs.all():
			if sub.is_active() and sub.campaign_type == campaign_type:
				return True
		return False

	@property
	def get_referee(self):
		referee = self.user.referee
		if referee and not referee.user.business:
			return referee
		return False

	def has_promo_sub(self):
		try:
			self.promo_sub
		except ObjectDoesNotExist:
			return False
		else:
			return self.promo_sub.is_active()			
