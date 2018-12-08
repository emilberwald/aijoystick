import platform
import logging

import numpy as np
import mss
import cv2

import utils_logging
from window_finder import get_window_handles

if platform.system() == 'Windows':
	from screenshot_windows import get_windowshot


def show_screenshot(shot, wait_ms=1000):
	if len(shot):
		bgrshot = cv2.cvtColor(shot, cv2.COLOR_RGB2BGR)
		cv2.imshow("{0}".format(shot), bgrshot)
		cv2.waitKey(wait_ms)
		cv2.destroyAllWindows()


@utils_logging.log_args
def get_screenshots(window_handles=None):
	"""Function that seeks windows to snap/screenshot
	Several optionals can be used to try to find windows more robustly -- a generator of screenshots is returned.
	NOTE: Since it yields the screenshots it is only iterable once.
	TODO: Separate the logic for which hwnds to check and yielding screenshots. Perhaps use sets ?
	"""

	@utils_logging.log_args
	def monitor_screenshots():
		#[https://pypi.org/project/mss/]
		with mss.mss() as multiple_screen_shot:
			for monitor in multiple_screen_shot.monitors:
				sct = multiple_screen_shot.grab(monitor)
				yield np.frombuffer(sct.rgb, dtype='uint8').reshape(sct.height, sct.width, 3)

	try:
		if window_handles:
			for window_handle in window_handles:
				yield get_windowshot(window_handle)
			return
	except Exception as exception:
		logging.error(exception)
		raise
	for shot in monitor_screenshots():
		yield shot
	return
