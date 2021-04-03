from types import ModuleType
from django.urls import path
from functools import wraps
from django.utils.decorators import method_decorator

try:
    from rest_framework.serializers import ValidationError
except:
    ImportError
    from django.core.exceptions import ValidationError
class Controller:
    app_name = None
    namespace = None
    instance = None

    def __new__(cls):
        urlconf_module = ModuleType(cls.__name__)
        urlpatterns = []

        instance = cls.get_instance()
            
        for attribute in dir(cls):
            value = getattr(cls, attribute)
            if getattr(value, "route", False) and callable(value):
                instance_value = getattr(instance, attribute)
                urlpatterns.append(path("%s/" % getattr(value, "route", ""), instance_value))
        urlconf_module.urlpatterns = urlpatterns
            
        return (
            urlconf_module,
            cls.app_name,
            cls.namespace
        )

    def validate_form(self, form):
        if not form.is_valid():
            raise ValidationError(form.errors.as_data(), code=400)

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = super().__new__(cls)
            cls.instance.__init__()
        return cls.instance

    @classmethod
    def route(cls, route_path=""):

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return (func(*args, **kwargs))
            setattr(wrapper, "route", (route_path or func.__name__))
            return wrapper
        return decorator

    @classmethod
    def unwrap_partials(cls):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                original_module = func.func.__module__
                original_name = func.func.__name__
                func.__module__ = original_module
                func.__name__ = original_name
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @classmethod
    def decorate(cls, *args):
        def decorator(func):
            arguments = list(args)
            arguments.append(cls.unwrap_partials())
            return method_decorator(arguments)(func)
        return decorator

