from django.test import TestCase
from utils.tests import TestMixin
from faker import Faker
from ..services import CampaignService
from ..models import Campaign, CampaignSub, Publisher

class TestCampaignService(TestCase, TestMixin):
	def setUp(self):
		self.faker = Faker()
		self.user = self.make_user()
		self.user.save()
		self.service = CampaignService()
	def make_user(self):
		faker = self.faker
		user_data = {
			'email': faker.email(), 
			'password': faker.password(), 
			'first_name': faker.first_name(), 
			'last_name': faker.last_name()
		}
		return User.objects.create(**user_data)

	def test_create_subscription(self, data):
		publisher = Publisher.objects.create()
		self.user.publisher = publisher
		self.user.save()
		minimum_amounts = [plan.min for plan in CampaignSub.AVAILABLE_PLANS]
		max_amounts = [plan.max for plan in CampaignSub.AVAILABLE_PLANS]
		available_amounts = [i for i in range(min(mimimum_amounts), max(maximum_amounts) + 500, 500)] 
		data = {
			'publisher': publisher,
			'principal': self.faker.random_element(available_amounts),
			'campaign_type': self.faker.random_element(Campaign.CAMPAIGN_TYPES)[0],
			
		}