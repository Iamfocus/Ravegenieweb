from django.test import TestCase, override_settings
from utils.tests import TestMixin
from django.test.client import Client
from django.contrib.auth import get_user_model
import json
from faker import Faker

User = get_user_model()

class TestUserCrud(TestCase, TestMixin):
	
	def setUp(self):
		self.faker = Faker()
		user_data = {
			'email': 'me@example.com', 
			'password': 'inlocoparentis156', 
			'first_name': 'hiz', 
			'last_name': 'dynasty'
		}
		self.auth_user = User.objects.create(**user_data)
		self.auth_user.set_password(user_data['password'])
		self.auth_user.is_staff = True
		self.auth_user.save()  # making the created user admin
		self.auth_user.refresh_from_db()
		self.client = Client()  # normal client
		self.auth_client = Client()  # authenticated client
		self.auth_client.login(username=user_data['email'], password=user_data['password'])


	def generate_users(self, number=10):
		generated = []
		faker = self.faker
		for i in range(number):
			user_data = {
				'email': faker.email(), 
				'password': faker.password(), 
				'first_name': faker.first_name(), 
				'last_name': faker.last_name()
			}
			user = User.objects.create(**user_data)
			generated.append(user)
		return generated

	def test_get_users(self):
		users = self.generate_users(3)
		user_data = [user.get_dict() for user in users]
		user_data.append(self.auth_user.get_dict())
		response = self.client.get('/users/get/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertResponseStatus(response, False) # unauthorized
		response = self.auth_client.get('/users/get/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		content = json.loads(response.content)
		self.assertResponseStatus(response, True)
		self.assertEqual(type(content['data'][0]), dict)
		#self.assertIn(user_data, content['data'])


	def test_user_self_update(self):
		update_data = {
			"first_name": self.faker.first_name(),
			"last_name": self.faker.last_name()
		}
		response = self.auth_client.post("/users/self-update/", update_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertResponseStatus(response, True)
		self.auth_user.refresh_from_db()
		self.assertEqual(self.auth_user.first_name, update_data["first_name"])
		self.assertEqual(self.auth_user.last_name, update_data["last_name"])



	def test_admin_update_user(self):
		user = self.generate_users(1)[0]
		user.is_blocked = False
		update_data = {"is_blocked": True}
		user.save()
		response = self.auth_client.post(
			f"/users/admin-update/{user.id}/", 
			update_data, 
			HTTP_X_REQUESTED_WITH='XMLHttpRequest'
		)
		self.assertResponseStatus(response, True)
		user.refresh_from_db()
		for key, value in update_data.items():
			self.assertEqual(getattr(user, key), value)


	def test_delete_user(self):
		user = self.generate_users(1)[0]
		response = self.auth_client.delete(f"/users/delete/{user.id}/", HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertResponseStatus(response, True)
		with self.assertRaises(User.DoesNotExist):
			User.objects.get(id=user.id)



