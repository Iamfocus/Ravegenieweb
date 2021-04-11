from django import forms
from .models import Campaign, CampaignSub, PromoSubscriptions, Promotion, PromotionSpec, User, Business
from django.utils import timezone
from django.conf import settings
import json
from json import JSONDecodeError

class UserUpdateForm(forms.Form):
	first_name = forms.CharField(max_length=50, required=False)
	last_name = forms.CharField(max_length=50, required=False)

class AdminUserUpdateForm(forms.Form):
	is_blocked = forms.BooleanField()
	
class DepositForm(forms.Form):
	amount = forms.DecimalField(required=True)
class WithdrawalForm(forms.Form):
	amount = forms.DecimalField(required=True)
class CampaignSubscriptionForm(forms.Form):
	principal = forms.DecimalField(required=True)
	type = forms.ChoiceField(choices=Campaign.CAMPAIGN_TYPES)

	def clean_principal(self):
		principal = self.cleaned_data['principal']
		if principal < CampaignSub.MINIMUM_SUB:
			raise forms.ValidationError(
				"amount must be greater than {}".format(str(CampaignSub.MINIMUM_SUB))
			)
		return principal


class PublisherBankUpdateForm(forms.Form):
	bank_account_no = forms.IntegerField(required=False)
	bank_name = forms.CharField(max_length=25, required=False)
	coin_type = forms.CharField(max_length=3, required=False)
	wallet_address = forms.CharField(max_length=64, required=False)

class StartCampaignForm(forms.Form):
	campaign_id = forms.IntegerField(required=True)
	subscription_id = forms.IntegerField(required=True)

	def clean_campaign_id(self):
		campaign_id = self.cleaned_data['campaign_id']
		if not Campaign.objects.get(id=campaign_id).exists():
			raise forms.ValidationError("no such campaign exists")
		return campaign_id

	def clean_subscription_id(self):
		subscription_id = self.cleaned_data['subscription_id']
		if not CampaignSub.objects.get(id=subscription_id).exists():
			raise forms.ValidationError("you are not subscribed to this")
		return campaign_id

class PromoSubscribeForm(forms.Form):
	package = forms.ChoiceField(choices=PromoSubscriptions.PACKAGES)

class StartPromotion(forms.Form):
	promotion_id = forms.IntegerField()

	def clean_promotion_id(self):
		promotion_id = self.cleaned_data['promotion_id']
		if not Promotion.objects.get(id=promotion_id).exists():
			raise forms.ValidationError("Promotion does not exist.")
			
class AddPromotion(forms.Form):
	promotion_spec_id = forms.IntegerField()
	promotion_link = forms.URLField()
	cost = forms.DecimalField(decimal_places=2)
	end_date = forms.DateTimeField()

	def clean_promotion_spec_id(self):
		id = self.cleaned_data['promotion_spec_id']
		try:
			spec = PromotionSpec.objects.get(id=id)
		except PromotionSpec.DoesNotExist:
			raise forms.ValidationError('promotion does not exist')
		else:
			self.cleaned_data['spec'] = spec
			
	
	def clean(self):
		data = super().clean()
		duration = data['end_date'] - timezone.now()
		cost = data['cost']
		spec = data.pop('spec')
		if cost < spec.cost() * duration.days:
			raise forms.ValidationError('Payment insufficient')

class AddCampaign(forms.Form):
	business_id = forms.IntegerField(required=False)
	end_date = forms.DateTimeField()
	cost = forms.DecimalField()
	ad = forms.Textarea()
	ad_image = forms.ImageField(required=False)
	campaign_type = forms.ChoiceField(choices=Campaign.CAMPAIGN_TYPES)
	
	def business_has_exclusive_spots(self, business_id):
		business = Business.objects.get(id=business_id)
		return (business.is_exclusive() and 
					business.exclusive_spots_used < settings.CAMPAIGNS_PER_EXCLUSIVE_SUB)

	def clean(self):
		data = super().clean()
		if self.business.has_exclusive_spots(data['business_id']):
			return
		duration = data['end_date'] - timezone.now()
		cost = data['cost']
		if cost < settings.CAMPAIGN_DAILY_PRICE * duration.days:
			raise forms.ValidationError('Payment insufficient')

class CreateNotification(forms.Form):
	subject = forms.Textarea()
	body = forms.Textarea()
	mail = forms.BooleanField(required=False)
	recipients = forms.CharField()

	def clean_recipients(self):
		recipient_ids = self.cleaned_data['recipients']
		try:
			recipient_ids = json.loads(recipient_ids)
		except JSONDecodeError:
			raise forms.ValidationError('Recipient list must be valid json')
		recipient_ids = [int(id) for id in recipient_ids]
		recipients = User.objects.filter(id__in=recipient_ids)
		if not recipients:
			raise forms.ValidationError('Invalid recipients')
		return recipients



		