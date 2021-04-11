from typing import Callable as function
from functools import wraps

def single_decorator(func):
	print("called 1st")
	
	def inner(*args, **kwargs):
		return func("single decor")
	return inner

def nested_decorator(flag):
	print("called 2nd")

	def wrapper(func):		
		def inner(*args, **kwargs):
			return func("nested decor") if flag else func(*args, **kwargs)
		return inner
	return wrapper

def wrapper(flag, decors):
	def inner(func):
		first = decors.pop(0)
		final = first(func)
		for decor in decors:	
			final = wraps(func)(decor(final))
		return final
	return inner

@wrapper(True, [nested_decorator(True), single_decorator])
def thefunc(arg)->None:
	print(arg)
	
@single_decorator
@nested_decorator(True)
def crase(arg: function)->bool:
	return arg

print(crase("air"))
