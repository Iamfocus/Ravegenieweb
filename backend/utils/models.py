from django.db import models
from hashlib import sha256
from django import forms
from django.core import exceptions
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
import json as simplejson
from django.utils.translation import ugettext_lazy as _
from .shortcuts import update_obj

class PasswordField(models.CharField):
    def __init__(self, **kwargs):
        self.char_field = models.CharField(editable=False, max_length=64, **kwargs)
    
    def __get__(self, instance, owner):
        return self.char_field
    
    def __set__(self, instance, value):
        hasher = sha256()
        hasher.update(value)
        self.char_field = hasher.hexdigest()

    def __eq__(self, other):
        if other is PasswordField:
            return self.char_field == other.char_field
        else:
            hasher = sha256()
            hasher.update(other)
            return self.char_field == hasher.hexdigest()
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __getattribute__(self, name):
        return object.__getattribute__(self, "char_field").__getattribute__(name)

class ModelMixin():
    Fillable = set([])
    Guarded = set([])

    def get_time_string(self, date):
        if not date: 
            return date
        return str(date)


    def update(self, **data):
        data = self._strip_dict(data)
        if len(data) < 1:
            raise Exception('Invalid update data')
        update_obj(self, data)
        self.save()

    def _strip_dict(self, data):
        data = self._strip_empty(data)
        data = self._remove_nonfillable(data)
        data = self._strip_guarded(data)
        return data

    def _remove_nonfillable(self, data):
        if not self.__class__.Fillable:
            return data
        for key in list(data.keys()):
            if key not in self.__class__.Fillable:
                data.pop(key)
        return data

    def _strip_empty(self, data):
        for key in list(data.keys()):
            if not data[key]:
                data.pop(key)
        return data

    def _strip_guarded(self, data):
        if not self.__class__.Guarded:
            return data
        for key in list(data.keys()):
            if key in self.__class__.Guarded:
                data.pop(key)
        return data
    


class DictionaryField(models.Field):
    description = _("Dictionary object")
    
    

    def get_internal_type(self):
        return "TextField"

    def to_python(self, value):
        if value is None:
            return None
        elif value == "":
            return {}
        elif isinstance(value, str):
            try:
                return dict(simplejson.loads(value))
            except (ValueError, TypeError):
                raise exceptions.ValidationError(self.error_messages['invalid'])
        
        if isinstance(value, dict):
            return value
        else:
            return {}
        
    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_prep_value(self, value):
        if not value:
            return ""
        elif isinstance(value, str):
            return value
        else:
            return simplejson.dumps(value)
            
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)
    
    def clean(self, value, model_instance):
        value = super(DictionaryField, self).clean(value, model_instance)
        return self.get_prep_value(value)
    
    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(DictionaryField, self).formfield(**defaults)



class ListField(models.Field):
    description = _("List object")
    
    

    def get_internal_type(self):
        return "TextField"

    def to_python(self, value):
        if value is None:
            return None
        elif value == "":
            return []
        elif isinstance(value, str):
            try:
                return list(simplejson.loads(value))
            except (ValueError, TypeError):
                raise exceptions.ValidationError(self.error_messages['invalid'])
        
        if isinstance(value, list):
            return value
        else:
            return []
        
    def from_db_value(self, value, expression, connection):
        return self.to_python(value)
        
    def get_prep_value(self, value):
        if not value:
            return ""
        elif isinstance(value, str):
            return value
        else:
            return simplejson.dumps(value)
            
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)
    
    def clean(self, value, model_instance):
        value = super(DictionaryField, self).clean(value, model_instance)
        return self.get_prep_value(value)
    
    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(DictionaryField, self).formfield(**defaults)
