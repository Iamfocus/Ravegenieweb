from django.urls import path
from . import controllers


urlpatterns = [
    path("example/", controllers.ExampleController()),
    path("flutter/", controllers.FlutterController()),
    path("users/", controllers.UserController()),
    path("transactions/", controllers.TransactionController()),
    path("business/", controllers.BusinessController()),
    path("notifications/", controllers.NotificationController()),
    path("publisher/", controllers.PublisherController()),
]