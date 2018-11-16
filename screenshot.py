import platform
import re
from collections import namedtuple
import logging
import numpy as np
import mss
import cv2

LOG_FORMAT_STRING = '[%(asctime)s][%(relativeCreated)07dms][%(processName)s:%(threadName)s][%(name)s:%(levelname)s][%(pathname)s:%(lineno)s][%(funcName)s]\n\t%(message)s'
STREAM_FORMATTER = logging.Formatter(LOG_FORMAT_STRING)
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setFormatter(STREAM_FORMATTER)
HTML_FORMATTER = logging.Formatter(
	fmt='<details>\n\t<summary><samp>' + LOG_FORMAT_STRING +
	'</samp></summary>\n\t<div><div class="processName">%(processName)s</div><div class="process">%(process)s</div><div class="threadName">%(threadName)s</div><div class="thread">%(thread)s</div><div class="name">%(name)s</div><div class="levelname">%(levelname)s</div><div class="levelno">%(levelno)s</div><div class="created">%(created)s</div><div class="msecs">%(msecs)s</div><div class="asctime">%(asctime)s</div><div class="relativeCreated">%(relativeCreated)s</div><div class="pathname">%(pathname)s</div><div class="lineno">%(lineno)s</div><div class="filename">%(filename)s</div><div class="module">%(module)s</div><div class="funcName">%(funcName)s</div><div class="message">%(message)s</div></div>\n</details>'
)
HTML_HANDLER = logging.FileHandler(f'{__name__}_log.html', mode='w')
HTML_HANDLER.setFormatter(HTML_FORMATTER)
logging.basicConfig(level=logging.NOTSET, handlers=[STREAM_HANDLER, HTML_HANDLER])

from logging_utils import log_args

if platform.system().lower() == 'windows':
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

	def get_window_name(hwnd):
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

	def get_window_class_name(hwnd, max_nof_bytes_class_name=32):
		"""
		:param hwnd: window handle
		:param max_nof_bytes_class_name: [description], defaults to 32
		:param max_nof_bytes_class_name: int, optional
		:return: Name of the window class that the specified window belongs to.
		"""

		windows_class_name_buffer = ctypes.create_unicode_buffer(max_nof_bytes_class_name)
		assert_win(ctypes.windll.user32.GetClassNameW(hwnd, windows_class_name_buffer, max_nof_bytes_class_name))
		return windows_class_name_buffer.value

	def get_window_handle_information():
		"""Retrieves information such as window_handle, process_id and thread_id.
	
		:return: a named tuple with window_handle, process_id and thread_id
		"""

		information = list()
		Information = namedtuple('Information', ['window_handle', 'process_id', 'thread_id'])

		def EnumWindowsProc(hwnd, lParam):
			window_process_id = ctypes.wintypes.DWORD()
			thread_id = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_process_id))

			information.append(Information(window_handle=hwnd, process_id=window_process_id.value, thread_id=thread_id))
			#To continue enumeration, the callback function must return TRUE;
			#to stop enumeration, it must return FALSE.
			return True

		assert_win(
			ctypes.windll.user32.EnumWindows(
			ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)(EnumWindowsProc), 0))

		return information

	def get_window_handle(window_name=None, window_class_name=None):
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

	@log_args
	def get_windowshot(window_handle):
		"""Get an RGB screen capture of a window

		:param window_handle: Handle to the window that will be screenshot.
		:type window_handle: ctypes.wintypes.HWND
		:return: RGB-screenshot
		:rtype: numpy.array
		"""

		class Context():
			"""
			Class to aid with creating and destroying the used resources in Windows.
			"""

			def __init__(self, *args, constructor=None, destructor=None, construct_ok=lambda x: x, destruct_ok=lambda x: x):
				self.constructor = constructor
				self.args = args
				self.construct = None
				self.destruct = None
				self.construct_ok = construct_ok
				self.destructor = destructor
				self.destruct_ok = destruct_ok

			def __enter__(self):
				if self.constructor:
					self.construct = self.constructor(*self.args)
					assert_win(self.construct_ok(self.construct))
				return self

			def __call__(self):
				return self.construct

			def __exit__(self, *exc_args):
				if self.destructor:
					self.destruct = self.destructor(self.construct)
					assert_win(self.destruct_ok(self.destruct))
				return False

		class BITMAPINFOHEADER(ctypes.Structure):
			_fields_ = [
				('biSize', ctypes.wintypes.DWORD),
				('biWidth', ctypes.wintypes.LONG),
				('biHeight', ctypes.wintypes.LONG),
				('biPlanes', ctypes.wintypes.WORD),
				('biBitCount', ctypes.wintypes.WORD),
				('biCompression', ctypes.wintypes.DWORD),
				('biSizeImage', ctypes.wintypes.DWORD),
				('biXPelsPerMeter', ctypes.wintypes.LONG),
				('biYPelsPerMeter', ctypes.wintypes.LONG),
				('biClrUsed', ctypes.wintypes.DWORD),
				('biClrImportant', ctypes.wintypes.DWORD),
			]

		class BITMAPINFO(ctypes.Structure):
			_fields_ = [
				('bmiHeader', BITMAPINFOHEADER),
				('bmiColors', ctypes.wintypes.DWORD * 3),
			]

		with Context(
			window_handle,
			constructor=ctypes.windll.user32.GetWindowDC,
			destructor=lambda hDC, hWnd=window_handle: ctypes.windll.user32.ReleaseDC(hWnd, hDC)) as ctx_window_device_context:
			with Context(
				ctx_window_device_context(), constructor=ctypes.windll.gdi32.CreateCompatibleDC,
				destructor=ctypes.windll.gdi32.DeleteDC) as ctx_memory_device_context_handle:

				window_rect = ctypes.wintypes.RECT()
				assert_win(ctypes.windll.user32.GetWindowRect(window_handle, ctypes.byref(window_rect)))
				width = window_rect.right - window_rect.left
				height = window_rect.bottom - window_rect.top
				with Context(
					ctx_window_device_context(),
					width,
					height,
					constructor=ctypes.windll.gdi32.CreateCompatibleBitmap,
					destructor=ctypes.windll.gdi32.DeleteObject) as ctx_graphics_device_interface_bitmap_handle:
					graphics_device_interface_previously_selected_bitmap_handle = ctypes.windll.gdi32.SelectObject(
						ctx_memory_device_context_handle(), ctx_graphics_device_interface_bitmap_handle())
					assert_win(graphics_device_interface_previously_selected_bitmap_handle)
					assert graphics_device_interface_previously_selected_bitmap_handle != ctypes.wintypes.HANDLE(0xFFFFFFFF)
					assert_win(ctypes.windll.user32.PrintWindow(window_handle, ctx_memory_device_context_handle(), 0))
					#[https://msdn.microsoft.com/sv-se/02f8ed65-8fed-4dda-9b94-7343a0cfa8c1,
					# https://msdn.microsoft.com/en-us/library/dd183376(v=vs.85).aspx]
					bitmap_info = BITMAPINFO()
					bitmap_info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
					bitmap_info.bmiHeader.biWidth = width
					#Top-down image [https://msdn.microsoft.com/sv-se/library/ms787796.aspx,
					# https://docs.microsoft.com/sv-se/windows/desktop/api/wingdi/nf-wingdi-getdibits]
					bitmap_info.bmiHeader.biHeight = -height
					bitmap_info.bmiHeader.biPlanes = 1
					#"The bitmap has a maximum of 2^32 colors. If the biCompression member of the BITMAPINFOHEADER is BI_RGB, the bmiColors
					# member of BITMAPINFO is NULL. Each DWORD in the bitmap array represents the relative intensities of blue, green, and
					# red for a pixel. The value for blue is in the least significant 8 bits, followed by 8 bits each for green and red.
					# The high byte in each DWORD is not used."
					# => Do not set bmiColors in ctypes?
					bitmap_info.bmiHeader.biBitCount = 32
					#"BI_RGB An uncompressed format." [wingdi.h]
					bitmap_info.bmiHeader.biCompression = 0
					#"This may be set to zero for BI_RGB bitmaps."
					bitmap_info.bmiHeader.biSizeImage = 0
					#0? 10 pixels/millimeter = 10000 pixels/m? -- no idea if there is a "correct" value
					bitmap_info.bmiHeader.biXPelsPerMeter = 0
					bitmap_info.bmiHeader.biYPelsPerMeter = 0
					#"If this value is zero, the bitmap uses the maximum number of colors corresponding to the value of the biBitCount
					# member for the compression mode specified by biCompression."
					bitmap_info.bmiHeader.biClrUsed = 0
					#"If this value is zero, all colors are required."
					bitmap_info.bmiHeader.biClrImportant = 0

					data = ctypes.create_string_buffer(width * height * 4)
					#[https://docs.microsoft.com/sv-se/windows/desktop/api/wingdi/nf-wingdi-getdibits]
					#DIB_RGB_COLORS = 0 [wingdi.h]
					nof_scanlines = ctypes.windll.gdi32.GetDIBits(ctx_memory_device_context_handle(),
						ctx_graphics_device_interface_bitmap_handle(), 0, height, data,
						bitmap_info, 0)
					assert_win(nof_scanlines == height)
					#Convert BGRX to RGB
					#https://stackoverflow.com/a/37421379
					return np.frombuffer(data, dtype='uint8').reshape(height, width, 4)[..., :3][..., ::-1]


@log_args
def get_window_handles(window_handle=None,
	window_name=None,
	window_class_name=None,
	window_name_regex=None,
	window_class_name_regex=None,
	process_id=None):
	if platform.system().lower() == "windows":
		try:
			hwnds = set()
			if window_handle:
				hwnds.add(window_handle)
			if window_name or window_class_name:
				hwnds.add(get_window_handle(window_name=window_name, window_class_name=window_class_name))
			if process_id or window_name_regex or window_class_name_regex:
				information = get_window_handle_information()
				for info in information:
					if process_id == info.process_id:
						logging.debug(f"[{info}]")
						hwnds.add(info.window_handle)
					if window_name_regex:
						window_name = get_window_name(info.window_handle)
						if re.match(window_name_regex, window_name):
							logging.debug(f"[{info}][window_name:{window_name}]")
							hwnds.add(info.window_handle)
					if window_class_name_regex:
						window_class_name = get_window_class_name(info.window_handle)
						if re.match(window_class_name_regex, window_class_name):
							logging.debug(f"[{info}][window_class_name:{window_class_name}]")
							hwnds.add(info.window_handle)
			return hwnds
		except Exception as exception:
			logging.error(exception)
			raise


@log_args
def get_screenshots(window_handles=None):
	"""Function that seeks windows to snap/screenshot
	Several optionals can be used to try to find windows more robustly -- a generator of screenshots is returned.
	NOTE: Since it yields the screenshots it is only iterable once.
	TODO: Separate the logic for which hwnds to check and yielding screenshots. Perhaps use sets ?
	"""

	@log_args
	def monitor_screenshots():
		#[https://pypi.org/project/mss/]
		with mss.mss() as multiple_screen_shot:
			for monitor in multiple_screen_shot.monitors:
				sct = multiple_screen_shot.grab(monitor)
				yield np.frombuffer(sct.rgb, dtype='uint8').reshape(sct.height, sct.width, 3)

	try:
		if window_handles:
			if platform.system().lower() == "windows":
				for window_handle in window_handles:
					logging.info(
						f'[{window_handle}][window_name:{get_window_name(window_handle)}][window_class_name:{get_window_class_name(window_handle)}]'
					)
					yield get_windowshot(window_handle)
				return
	except Exception as exception:
		logging.error(exception)
		raise
	for shot in monitor_screenshots():
		yield shot
	return


if __name__ == "__main__":
	try:
		SHOTS = get_screenshots(get_window_handles(window_name_regex=".*Notepad.*"))
		for shot in SHOTS:
			logging.info("Got shot.")
			if len(shot):
				logging.info("Shot can be drawn.")
				bgrshot = cv2.cvtColor(shot, cv2.COLOR_RGB2BGR)
				cv2.imshow("{0}".format(shot), bgrshot)
				cv2.waitKey(1000)
				cv2.destroyAllWindows()
	except Exception as exception:
		logging.error(exception)
		raise
	finally:
		logging.info("THE END")
