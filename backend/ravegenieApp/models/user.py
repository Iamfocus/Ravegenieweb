from . import modelmanagers
from django.db import models, IntegrityError
from django.contrib.auth.base_user import AbstractBaseUser
from utils.models import ModelMixin
from .business import Business
from .publisher import Publisher
from utils.code_generator import generate_code

class User(AbstractBaseUser, ModelMixin):
	class Meta:
		ordering = ["-created_at"]

	PUBLISHER = 'P'
	BUSINESS = 'B'
	TYPES = (
		(BUSINESS, 'business'),
		(PUBLISHER, 'publisher')
	)
	Guarded = set(["is_staff", "is_superuser", "password", "referral_id"])

	email = models.EmailField(unique=True)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	is_superuser = models.BooleanField(default=False)
	is_blocked = models.BooleanField(default=False)
	is_staff = models.BooleanField(default=False)
	referee = models.ForeignKey("self", null=True, on_delete=models.SET_NULL, related_name='referrals')
	created_at = models.DateTimeField(auto_now_add=True)
	business = models.OneToOneField(Business, on_delete=models.DO_NOTHING, related_name='user', null=True)
	publisher = models.OneToOneField(Publisher, on_delete=models.DO_NOTHING, related_name='user', null=True)
	referral_id = models.CharField(max_length=20, unique=True)

	EMAIL_FIELD = "email"
	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ["first_name", "last_name"]
	objects = modelmanagers.UserManager()

	def get_dict(self, ):
		return {
			"email": self.email,
			"firstName": self.first_name,
			"lastName": self.last_name,
			"isSuperuser": self.is_superuser,
			"isStaff": self.is_staff,
			"isBlocked": self.is_blocked,
			"referralId": self.referral_id,
			"notifications": self.get_notifications(),
			"referrals": self.referrals.count(),
		}
	
	def get_type(self):
		if self.business:
			return self.__class__.BUSINESS
		if self.publisher:
			return self.__class__.PUBLISHER
	
	def get_profile(self):
		return self.business or self.publisher

	def get_notifications(self):
		return [notification.get_dict for notification in self.notifications.all()]			

	def __str__(self):
		return "<{} {}, {}>".format(self.first_name, self.last_name, self.email)

	
	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		if not self.referral_id:
			return self._make_ref_id()

	def _make_ref_id(self):
		while True:
			ref_id = generate_code(9)
			try:
				self.referral_id = ref_id
				self.save()
			except IntegrityError:
				continue
			else:
				break
	
	


