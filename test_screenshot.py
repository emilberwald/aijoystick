import unittest
from screenshot import *


class TestScreenshot(unittest.TestCase):
	def test_get_screenshots(self):
		try:
			handles = get_window_handles(window_name_regex=".*Notepad.*")
			SHOTS = get_screenshots(handles)
			for shot in SHOTS:
				logging.info("Got shot.")
				show_screenshot(shot)
		except Exception as exception:
			logging.error(exception)
			raise
		finally:
			logging.info("THE END")
