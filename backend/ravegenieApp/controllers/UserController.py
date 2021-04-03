from utils.controller import Controller
from utils.shortcuts import json_response, paginate
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from utils.decorators import ensure_signed_in, ensure_staff
from .. import forms


User = get_user_model()
class UserController(Controller):

	@Controller.route("get")
	@Controller.decorate(api_view(["GET"]), ensure_staff)
	def get_users(self, request):
		page = request.query_params.get("page", 1)
		query_set = User.objects.all()
		users, previous_page, next_page, num_of_pages = paginate(query_set, page)
		detailed_users = [user.get_dict() for user in users]
		return json_response(
			status=True,
			data=detailed_users,
			number_of_pages=num_of_pages,
			previous_page=previous_page,
			next_page=next_page,
		)

	@Controller.route("self-update")
	@Controller.decorate(ensure_signed_in)
	@Controller.decorate(api_view(["PATCH", "POST"]))
	def user_self_update(self, request):
		data = request.data.copy()
		form = forms.UserUpdateForm(data)
		self.validate_form(form)
		request.user.update(**form.cleaned_data)
		return json_response(status=True)


	@Controller.route("admin-update/<int:id>")
	@Controller.decorate(ensure_staff)
	@Controller.decorate(api_view(["PATCH", "POST"]))
	def admin_update(self, request, id):
		form = forms.AdminUserUpdateForm(request.data)
		self.validate_form(form)
		user = User.objects.get(id=id)
		user.update(**form.cleaned_data)
		return json_response(status=True)

	@Controller.route("delete/<int:id>")
	@Controller.decorate(ensure_staff)
	@Controller.decorate(api_view(["DELETE", "POST"]))
	def user_delete(self, request, id):
		User.objects.get(id=id).delete()
		return json_response(status=True)
		