from utils.controller import Controller
from utils.shortcuts import json_response, paginate
from ..models import Publisher, Campaign
from utils.decorators import ensure_staff, ensure_signed_in
from .. import forms
from ..services import CampaignService, PromotionService
from ..exceptions import TransactionError
from ravegenieApp.exceptions import PromotionError
from rest_framework.decorators import api_view

class PublisherController(Controller):
	def __init__(self):
		self.campaign_service = CampaignService()
		self.promotion_service = PromotionService()

	
	@Controller.route()
	@Controller.decorate(api_view(['GET']), ensure_signed_in)
	def ping(self, request):
		if request.user.business:
			return json_response(False, error="You are a business, not a publisher")
		publisher: Publisher = request.user.publisher
		if not publisher:
			publisher: Publisher = Publisher.objects.create(user=request.user)
			request.user.save()
		return json_response(True, data=publisher.get_dict())

	@Controller.route()
	@Controller.decorate(api_view(['GET']), ensure_signed_in)
	def get_campaign_subscriptions(self, request):
		publisher = request.user.publisher
		if not publisher.has_campaign_subs():
			return json_response(status=False, error='You have no active campaign subscriptions')	
		sub = [sub.get_dict() for sub in publisher.campaign_subs.all() ]
		return json_response(status=True, data=sub)
	
	@Controller.route()
	@Controller.decorate(api_view(['POST']), ensure_signed_in)
	def campaign_subscribe(self, request):
		publisher = request.user.publisher
		form = forms.CampaignSubscriptionForm(request.data)
		self.validate_form(form)
		try:
			subscription = self.campaign_service.create_subscription(publisher, form.cleaned_data)
		except Exception as e:
			return json_response(status=False, error=str(e))
		else:
			return json_response(status=True, data=subscription.get_dict())	
	
	@Controller.route()
	@Controller.decorate(api_view(['POST']), ensure_signed_in)
	def renew_campaign_subscription(self, request):
		subscription_id = request.GET.get('sub_id', None)
		if not subscription_id:
			return json_response(status=False, error="sub_id is required")			
		publisher = request.user.publisher
		try:
			subscription = self.campaign_service.renew_subscription(publisher, subscription_id)
		except Exception as e:
			return json_response(status=False, error=str(e))
		else:
			return json_response(status=True, data=subscription.get_dict())	
	
	@Controller.decorate()
	@Controller.decorate(api_view(['POST']), ensure_signed_in)
	def start_campaign(self, request):
		publisher: Publisher = request.user.publisher
		form = forms.StartCampaignForm(request.data)
		self.validate_form(form)
		sub_id = form.cleaned_data['subscription_id']
		campaign_id = form.cleaned_data['campaign_id']
		self.campaign_service.start_campaign(publisher, sub_id, campaign_id)
		return json_response(status=True)
	

	@Controller.route()
	@Controller.decorate(api_view(['GET']), ensure_signed_in)
	def get_campaigns(self, request):
		publisher: Publisher = request.user.publisher
		campaign_type = request.GET.get("pack", None)
		if not campaign_type:
			return json_response(status=False, error="pack must be specified")
		page = request.GET.get("page", 1)
		if not publisher.has_campaign_of_type(campaign_type):
			return json_response(status=False, error="You are not subscribed to this pack")
		query = self.campaign_service.get_publisher_campaigns(campaign_type, publisher)
		campaigns, previous_page, next_page, num_of_pages = paginate(query, page)
		campaign_details = [campaign.get_dict() for campaign in campaigns]
		return json_response(
			status=True, 
			data=campaign_details, 
			number_of_pages=num_of_pages,
			previous_page=previous_page,
			next_page=next_page
		)

	@Controller.route()
	@Controller.decorate(api_view(['POST']), ensure_signed_in)
	def update_bank_details(self, request):
		publisher: Publisher = request.user.publisher
		form = forms.PublisherBankUpdateForm(request.data)
		self.validate_form(form)
		publisher.update(**form.cleaned_data)
		return json_response(status=True)

	@Controller.route()
	@Controller.decorate(api_view(['POST']), ensure_signed_in)
	def subscribe_promotion(self, request):
		publisher: Publisher = request.user.publisher
		form = forms.PromoSubscribeForm(request.data)
		self.validate_form(form)
		try:
			subscription = self.promotion_service.subscribe(publisher, form.cleaned_data['package'])
		except TransactionError  as e:
			return json_response(False, error=str(e))
		else:
			return json_response(True, data={'subscription': subscription})
	
	@Controller.route()
	@Controller.decorate(api_view(['GET']), ensure_signed_in)
	def get_promotions(self, request):
		publisher: Publisher = request.user.publisher
		page = request.GET.get('page', 1)
		if not publisher.has_promo_sub():
			return json_response(False, error='You are not subscribed')
		query = self.promotion_service.get_promotions(publisher)
		promotions, previous_page, next_page, num_of_pages = paginate(query, page)
		promotion_details = [promotion.get_dict() for promotion in promotions]
		return json_response(
			status=True, 
			data=promotion_details, 
			number_of_pages=num_of_pages,
			previous_page=previous_page,
			next_page=next_page
		)
	
	@Controller.route()
	@Controller.decorate(api_view(['POST']), ensure_signed_in)
	def start_promotion(self, request):
		publisher: Publisher = request.user.publisher
		form = forms.StartPromotion(request.data)
		self.validate_form(form)
		try:
			self.promotion_service.start_promotion(publisher, form.cleaned_data['promotion_id'])
		except PromotionError as e:
			return json_response(False, error=str(e))
		else:
			return json_response(True)
	
	