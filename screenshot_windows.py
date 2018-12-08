"""[summary]

:return: [description]
:rtype: [type]
"""

import ctypes
import ctypes.wintypes

import numpy as np

import logging
import utils_logging

from utils_os import assert_win


class Context():
	"""
	Class to aid with creating and destroying the used resources in Windows.
	"""

	@utils_logging.log_call
	def __init__(self, *args, constructor=None, destructor=None, construct_ok=lambda x: x, destruct_ok=lambda x: x):
		self.constructor = constructor
		self.args = args
		self.construct = None
		self.destruct = None
		self.construct_ok = construct_ok
		self.destructor = destructor
		self.destruct_ok = destruct_ok

	@utils_logging.log_call
	def __enter__(self):
		if self.constructor:
			self.construct = self.constructor(*self.args)
			assert_win(self.construct_ok(self.construct))
		return self

	@utils_logging.log_call
	def __call__(self):
		return self.construct

	@utils_logging.log_call
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


@utils_logging.log_args
def get_windowshot(window_handle):
	"""Get an RGB screen capture of a window

	:param window_handle: Handle to the window that will be screenshot.
	:type window_handle: ctypes.wintypes.HWND
	:return: RGB-screenshot
	:rtype: numpy.array
	"""

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
				logging.debug('Contexts created.')
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
					ctx_graphics_device_interface_bitmap_handle(), 0, height, data, bitmap_info,
					0)
				assert_win(nof_scanlines == height)
				#Convert BGRX to RGB
				#https://stackoverflow.com/a/37421379
				return np.frombuffer(data, dtype='uint8').reshape(height, width, 4)[..., :3][..., ::-1]
