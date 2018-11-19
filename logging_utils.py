import inspect
import logging
from functools import wraps
import html


def log_args(decorated_function):
	"""Decorator to print function call details - parameters names and effective values.
	based on https://stackoverflow.com/a/6278457/3021108
    """

	@wraps(decorated_function)
	def log_args_wrapper(*args, **kwargs):
		func_args = inspect.signature(decorated_function).bind(*args, **kwargs).arguments
		func_args_str = ','.join('{}={!r}'.format(*item) for item in func_args.items())
		logging.debug(
			html.escape(
			f'[{decorated_function.__code__.co_filename}:{decorated_function.__code__.co_firstlineno}][{decorated_function.__module__}.{decorated_function.__qualname__}({func_args_str})]',
			True))
		return decorated_function(*args, **kwargs)

	return log_args_wrapper


def log_call(decorated_function):
	@wraps(decorated_function)
	def log_call_wrapper(*args, **kwargs):
		func_args = inspect.signature(decorated_function).bind(*args, **kwargs).arguments
		func_args_str = ','.join('{}={!r}'.format(*item) for item in func_args.items())
		logging.debug(
			html.escape(
			f'[{decorated_function.__code__.co_filename}:{decorated_function.__code__.co_firstlineno}][{decorated_function.__module__}.{decorated_function.__qualname__}({func_args_str})]',
			True))
		retval = decorated_function(*args, **kwargs)
		logging.debug(html.escape(f"-> {retval}", True))
		return retval

	return log_call_wrapper


LOG_FORMAT_STRING = '[%(asctime)s][%(relativeCreated)07dms][%(processName)s:%(threadName)s][%(name)s:%(levelname)s][%(pathname)s:%(lineno)s][%(funcName)s]\n\t%(message)s'
STREAM_FORMATTER = logging.Formatter(LOG_FORMAT_STRING)
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(STREAM_FORMATTER)
HTML_FORMATTER = logging.Formatter(
	fmt='<details>\n\t<summary><samp>' + LOG_FORMAT_STRING +
	'</samp></summary>\n\t<div><div class="processName">%(processName)s</div><div class="process">%(process)s</div><div class="threadName">%(threadName)s</div><div class="thread">%(thread)s</div><div class="name">%(name)s</div><div class="levelname">%(levelname)s</div><div class="levelno">%(levelno)s</div><div class="created">%(created)s</div><div class="msecs">%(msecs)s</div><div class="asctime">%(asctime)s</div><div class="relativeCreated">%(relativeCreated)s</div><div class="pathname">%(pathname)s</div><div class="lineno">%(lineno)s</div><div class="filename">%(filename)s</div><div class="module">%(module)s</div><div class="funcName">%(funcName)s</div><div class="message">%(message)s</div></div>\n</details>'
)
if __name__ == '__main__':
	FILE_NAME = __name__
else:
	for frame in inspect.stack()[1:]:  #exclude current frame, check the callers
		if frame.filename[0] != '<':  #libraries have '<' in filename
			FILE_NAME = frame.filename
			break
HTML_HANDLER = logging.FileHandler(f'{FILE_NAME}_log.html', mode='w')
HTML_HANDLER.setFormatter(HTML_FORMATTER)
logging.basicConfig(level=logging.NOTSET, handlers=[STREAM_HANDLER, HTML_HANDLER])
