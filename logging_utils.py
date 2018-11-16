import inspect
import logging
from functools import wraps


def log_args(decorated_function):
	"""Decorator to print function call details - parameters names and effective values.
	based on https://stackoverflow.com/a/6278457/3021108
    """

	@wraps(decorated_function)
	def log_args_wrapper(*args, **kwargs):
		func_args = inspect.signature(decorated_function).bind(*args, **kwargs).arguments
		func_args_str = ','.join('{}={!r}'.format(*item) for item in func_args.items())
		logging.debug(
			f'[{decorated_function.__code__.co_filename}:{decorated_function.__code__.co_firstlineno}][{decorated_function.__module__}.{decorated_function.__qualname__}({func_args_str})]'
		)
		return decorated_function(*args, **kwargs)

	return log_args_wrapper
