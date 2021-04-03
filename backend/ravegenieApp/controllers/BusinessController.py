from utils.controller import Controller
from utils.shortcuts import json_response
from ..models import Business
from ..services import BusinessService, PromotionService, CampaignService
from ..exceptions import TransactionError
from rest_framework.decorators import api_view
from .. import forms

class BusinessController(Controller):
	def __init__(self):
		self.business_service = BusinessService()
	
	@Controller.route()
	@Controller.decorate(api_view(['GET']))
	def ping(self, request):
		if request.user.publisher:
			return json_response(False, error="You are a publisher, not a business")
		business: Business = request.user.business
		if not business:
			business: Business = Business.objects.create(user=request.user)
			request.user.save()
		return json_response(True, data=business.get_dict())
	
	@Controller.route()
	@Controller.decorate(api_view(['POST']))
	def upgrade_to_exclusive(self, request):
		business: Business = request.user.business
		try:
			self.business_service.subscribe_to_exclusive(business)
		except TransactionError as e:
			return json_response(False, error=str(e))
		else:
			return json_response(True)

	@Controller.route()
	@Controller.decorate(api_view(['POST']))
	def add_promotion(self, request):
		business: Business = request.user.business
		form = forms.AddPromotion(request.data)
		self.validate_form(form)
		data = form.cleaned_data
		promotion_service: PromotionService = PromotionService()
		promotion = promotion_service.create_promotion(
			business=business,
			cost=data['cost'],
			link=data['promotion_link'],
			promotion_spec=data['promotion_spec_id'],
			end_date=data['end_date']
		)
		return json_response(True, data=promotion.get_dict())


	@Controller.route()
	@Controller.decorate(api_view(['POST']))
	def add_campaign(self, request):
		business: Business = request.user.business
		data = request.data.copy()
		data['business_id'] = business.pk
		form = forms.AddCampaign(data, request.FILES)
		self.validate_form(form)
		campaign_service: CampaignService = CampaignService()
		campaign = campaign_service.create_campaign(business, **form.cleaned_data)
		return json_response(True, data=campaign.get_dict())
	
	@Controller.route()
	@Controller.decorate(api_view(['GET']))
	def get_campaigns(self, request):
		business: Business = request.user.business
		campaigns = business.campaigns.all()
		campaign_details = [campaign.get_dict() for campaign in campaigns]
		return json_response(True, data=campaign_details)
	
	@Controller.route()
	@Controller.decorate(api_view(['GET']))
	def get_promotions(self, request):
		business: Business = request.user.business
		promotions = business.promotions.all()
		promotion_details = [promotion.get_dict() for promotion in promotions]
		return json_response(True, data=promotion_details)

		

	



		