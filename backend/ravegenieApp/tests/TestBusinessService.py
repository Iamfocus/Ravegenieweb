from django.test import TestCase
from utils.tests import TestMixin
from faker import Faker
import decimal
from django.contrib.auth import get_user_model
from ..models import Business, Transaction, Campaign
from ..services import BusinessService
from ..exceptions import TransactionError
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

User = get_user_model()
class TestBusinessService(TestCase, TestMixin):
	def setUp(self):
		self.faker = Faker()
		self.user = self.make_user()
		self.user.business = Business.objects.create()
		self.user.save()
		self.business = self.user.business 
		self.service = BusinessService()

	def make_user(self):
		faker = self.faker
		user_data = {
			'email': faker.email(), 
			'password': faker.password(), 
			'first_name': faker.first_name(), 
			'last_name': faker.last_name()
		}
		return User.objects.create(**user_data)
	
	def make_decimal(self, number):
		return decimal.Decimal( 
			number
		).quantize(
			decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN
			)

	def test_attempt_exclusive_sub_without_balance(self):
		with self.assertRaises(TransactionError):
			self.service.subscribe_to_exclusive(self.business)

	def test_sub_to_exclusive(self):
		self.business.account_balance = settings.EXCLUSIVE_COST + 10
		initial_balance = self.business.account_balance
		self.business.save()
		self.service.subscribe_to_exclusive(self.business)
		self.business.refresh_from_db()
		self.assertEqual((initial_balance-settings.EXCLUSIVE_COST), self.business.account_balance)
		self.assertIsNotNone(self.business.exclusive_start_date)
		self.assertIsNotNone(self.business.exclusive_end_date)
		self.assertTrue(self.business.is_exclusive())
		query = Q(user=self.business.user) and Q(type=Transaction.DEBIT)
		self.assertTrue(Transaction.objects.filter(query).exists())

	def test_exclusive_subscribed_with_exclusive_ref(self):
		referee = self.make_user()
		ref_business = Business.objects.create(user=referee)
		referee.save()
		ref_business.exclusive_start_date = timezone.now()
		ref_business.save()
		self.business.user.referee = referee
		self.business.user.save()
		self.service.exclusive_subscribed(self.business)
		query = Q(user=referee) and Q(type=Transaction.BONUS)
		self.assertTrue(Transaction.objects.filter(query).exists())
		transaction = Transaction.objects.get(query)
		ref_business.refresh_from_db()
		self.assertEqual(ref_business.bonus_balance, transaction.dollar_amount)

		bonus_amount = self.make_decimal((settings.EXCLUSIVE_REF_BONUS / 100) * settings.EXCLUSIVE_COST)
		self.assertEqual(bonus_amount, transaction.dollar_amount)
	
	def test_exclusive_subscribed_without_exclusive_ref(self):
		refereee = self.make_user()
		ref_business = Business.objects.create(user=refereee)
		self.business.user.referee = refereee
		self.business.user.save()
		self.service.exclusive_subscribed(self.business)
		query = Q(user=refereee) and Q(type=Transaction.BONUS)
		self.assertTrue(Transaction.objects.filter(query).exists())
		transaction = Transaction.objects.get(query)
		ref_business.refresh_from_db()
		self.assertEqual(ref_business.bonus_balance, transaction.dollar_amount)
		bonus_amount = self.make_decimal((settings.BUSINESS_REF_BONUS / 100) * settings.EXCLUSIVE_COST)
		self.assertEqual(bonus_amount, transaction.dollar_amount)

	def test_compensate_exclusive_business_referee(self):
		refereee = self.make_user()
		ref_business = Business.objects.create(user=refereee)
		self.business.user.referee = refereee
		self.business.user.save()
		campaign = Campaign.objects.create(
			start_date=timezone.now(),
			raw_ad=self.faker.url(),
			business=self.business,
			cost=23
		)
		self.service.compensate_business_referees(campaign)
		ref_business.refresh_from_db()
		bonus_amount = self.make_decimal((settings.BUSINESS_REF_BONUS / 100) * campaign.cost)
		self.assertEqual(bonus_amount, ref_business.bonus_balance)
		query = Q(dollar_amount=bonus_amount) and Q(user=refereee)
		self.assertTrue(Transaction.objects.filter(query).exists())
		self.assertTrue(self.business.first_campaign_ref_paid)


