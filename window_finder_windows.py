"""
The purpose of this module is to help finding window handles.
"""

import platform
import re
from collections import namedtuple
import logging

import utils_logging

import ctypes
import ctypes.wintypes
from utils_os import assert_win


def __get_window_name(hwnd):
	"""
	:param hwnd: window handle
	:return: Window Text (title bar / control text)
	"""

	window_name_nof_bytes = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
	if window_name_nof_bytes:
		window_name_buffer = ctypes.create_unicode_buffer(window_name_nof_bytes + 1)
		length_excluding_null = ctypes.windll.user32.GetWindowTextW(hwnd, window_name_buffer, window_name_nof_bytes + 1)
		return window_name_buffer.value
	else:
		return ""


def __get_window_class_name(hwnd, max_nof_bytes_class_name=32):
	"""
	:param hwnd: window handle
	:param max_nof_bytes_class_name: [description], defaults to 32
	:param max_nof_bytes_class_name: int, optional
	:return: Name of the window class that the specified window belongs to.
	"""

	windows_class_name_buffer = ctypes.create_unicode_buffer(max_nof_bytes_class_name)
	assert_win(ctypes.windll.user32.GetClassNameW(hwnd, windows_class_name_buffer, max_nof_bytes_class_name))
	return windows_class_name_buffer.value


def __get_window_handle_information_for(window_handle):
	Information = namedtuple('Information', ['window_handle', 'process_id', 'thread_id'])
	window_process_id = ctypes.wintypes.DWORD()
	thread_id = ctypes.windll.user32.GetWindowThreadProcessId(window_handle, ctypes.byref(window_process_id))
	return Information(window_handle=window_handle, process_id=window_process_id.value, thread_id=thread_id)


def __get_window_handle_information():
	"""Retrieves information such as window_handle, process_id and thread_id.

	:return: a named tuple with window_handle, process_id and thread_id
	"""

	information = list()

	def EnumWindowsProc(hwnd, lParam):
		information.append(__get_window_handle_information_for(hwnd))
		#To continue enumeration, the callback function must return TRUE;
		#to stop enumeration, it must return FALSE.
		return True

	assert_win(
		ctypes.windll.user32.EnumWindows(
		ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)(EnumWindowsProc), 0))

	return information


def __get_window_handle(window_name=None, window_class_name=None):
	"""Searches for the window handle matching the window name
	or window class name.

	Uses
		https://docs.microsoft.com/en-us/windows/desktop/api/winuser/nf-winuser-findwindoww

	:param window_name: [description], defaults to None
	:param window_name: [type], optional
	:param window_class_name: [description], defaults to None
	:param window_class_name: [type], optional
	:return: matched window handle
	"""
	window_handle = ctypes.windll.user32.FindWindowW(ctypes.wintypes.LPCWSTR(window_class_name), ctypes.wintypes.LPCWSTR(window_name))
	assert_win(window_handle)
	return window_handle


def process_information(process_id):
	all_windows = __get_window_handle_information()
	result = dict()
	for info in all_windows:
		if info.process_id == process_id:
			result[info] = {
				'window_name': __get_window_name(info.window_handle),
				'window_class_name': __get_window_class_name(info.window_handle)
			}
	return result


def window_information(window_handle):
	return {
		__get_window_handle_information_for(window_handle): {
		'window_name': __get_window_name(window_handle),
		'window_class_name': __get_window_class_name(window_handle)
		}
	}


@utils_logging.log_call
def get_window_handles_from_cursor_position():
	def __window_from_point(point):
		function = ctypes.windll.user32.WindowFromPoint
		function.restype = ctypes.wintypes.HANDLE
		return assert_win(function(point))

	def __get_cursor_pos():
		function = ctypes.windll.user32.GetCursorPos
		function.restype = ctypes.wintypes.BOOL
		point = ctypes.wintypes.POINT()
		assert_win(function(ctypes.byref(point)))
		return point

	#ChildWindowFromPoint ScreenToClient
	return {__window_from_point(__get_cursor_pos())}


@utils_logging.log_call
def get_window_handles(window_handle=None,
	window_name=None,
	window_class_name=None,
	window_name_regex=None,
	window_class_name_regex=None,
	process_id=None):
	"""[summary]

	:param window_handle: [description], defaults to None
	:param window_handle: [type], optional
	:param window_name: [description], defaults to None
	:param window_name: [type], optional
	:param window_class_name: [description], defaults to None
	:param window_class_name: [type], optional
	:param window_name_regex: [description], defaults to None
	:param window_name_regex: [type], optional
	:param window_class_name_regex: [description], defaults to None
	:param window_class_name_regex: [type], optional
	:param process_id: [description], defaults to None
	:param process_id: [type], optional
	:return: [description]
	:rtype: [type]
	"""
	try:
		hwnds = set()
		if window_handle:
			hwnds.add(window_handle)
		if window_name or window_class_name:
			hwnds.add(__get_window_handle(window_name=window_name, window_class_name=window_class_name))
		if process_id or window_name_regex or window_class_name_regex:
			information = __get_window_handle_information()
			for info in information:
				if process_id == info.process_id:
					logging.debug(f"[{info}]")
					hwnds.add(info.window_handle)
				if window_name_regex:
					window_name = __get_window_name(info.window_handle)
					if re.match(window_name_regex, window_name):
						logging.debug(f"[{info}][window_name:{window_name}]")
						hwnds.add(info.window_handle)
				if window_class_name_regex:
					window_class_name = __get_window_class_name(info.window_handle)
					if re.match(window_class_name_regex, window_class_name):
						logging.debug(f"[{info}][window_class_name:{window_class_name}]")
						hwnds.add(info.window_handle)
		return hwnds
	except Exception as exception:
		logging.error(exception)
		raise
