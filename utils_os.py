import platform
import utils_logging

if platform.system() == 'Windows':
	import ctypes
	import ctypes.wintypes

	def assert_win(arg):
		"""
		:param arg: value to check
		:raises ctypes.WinError: if arg does not evaluate to True,
				raises an error with relevant information.
		:return: if arg evaluates to True, returns arg.
		"""

		if arg:
			return arg
		else:
			raise ctypes.WinError()

	@utils_logging.log_args
	def set_foreground_window(window_handle):
		assert_win(ctypes.windll.user32.SetForegroundWindow(window_handle))

	@utils_logging.log_args
	def get_foreground_window():
		return assert_win(ctypes.windll.user32.GetForegroundWindow())
