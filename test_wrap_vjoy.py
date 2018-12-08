import unittest
from wrap_vjoy import *


class TestVJoyDevice(unittest.TestCase):
	def test_no_errors(self):
		with VJoyDevice(report_id=1) as dev:
			axes = dev.get_available_axes()
			nof_buttons = dev.get_nof_buttons()
			nof_dhats = dev.get_nof_discrete_hats()
			nof_chats = dev.get_nof_continuous_hats()
			dev.reset()
			for axis in axes:
				for value in range(0x1, 0x8000 + 1, 0x8000 // 10):
					dev.set_axis(axis, value)
			for value in (False, True):
				for button_no in range(1, nof_buttons + 1):
					dev.set_button(button_no, value)
			dev.reset_buttons()
			for dhat in range(1, nof_dhats + 1):
				for value in list(VJoyDevice.DiscreteHatDirection):
					dev.set_discrete_hat(dhat, value)
			for chat in range(1, nof_chats + 1):
				for value in range(-1, 35999 + 1, 100):
					dev.set_continuous_hat(chat, value)
			dev.reset_hats()
			dev.reset()
