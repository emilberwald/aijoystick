"""[summary]

"""

import logging

import utils_logging
import wrap_vjoy
import window_finder
import screenshot
import utils_os
import cv2
import time

utils_logging.STREAM_HANDLER.setLevel(logging.INFO)


def get_option(*options):
	prompt = f'{options[:10]!r} ... {options[-10:]!r}> ' if len(options) > 10 else f'{options!r}> '
	choice = input(prompt)
	for option in options:
		try:
			casted = type(option)(choice)
			if casted == option:
				logging.info(f'chose {option!r} since {choice!r} ({casted!r})')
				return option
		except (
			ValueError,
			TypeError,
		) as e:
			pass
		try:
			casted = type(option.value)(choice)
			if casted == option.value:
				logging.info(f'chose {option!r} since {choice!r} ({casted!r})')
				return option
		except (
			ValueError,
			TypeError,
			AttributeError,
		) as e:
			pass
		try:
			casted = type(option.name)(choice)
			if casted == option.name:
				logging.info(f'chose {option!r} since {choice!r} ({casted!r})')
				return option
		except (
			ValueError,
			TypeError,
			AttributeError,
		) as e:
			pass
	for option in options:
		choice = input(f'choose {option!r} ?> ')
		if choice:
			logging.info('option {option!r} chosen')
			return option
	logging.warning('no option chosen')


class KeyBinder:
	def __init__(self):
		self.keybindings = dict()

	@staticmethod
	def repeat_press(function, *args, nof_times=5, sleep_time=1.0):
		for time_no in range(0, nof_times):
			logging.info(f'pressing {args} [{time_no}/{nof_times}]')
			function(*args)
			logging.info(f'sleeping {sleep_time}s...')
			time.sleep(sleep_time)

	@utils_logging.log_call
	def setup_controls(self, nof_times=5, sleepTime=1.0):
		def fix_keybinding(function, *args, **kwargs):
			name_of_keybinding = None
			while not name_of_keybinding:
				self.repeat_press(function, *args, **kwargs)
				name_of_keybinding = input('name of keybinding (empty to retry keypressing)> ')
				if name_of_keybinding:
					self.keybindings[name_of_keybinding] = utils_logging.call_entry_to_string(function, *args, **kwargs)
					logging.info(f'keybindings:{self.keybindings}')

		with wrap_vjoy.VJoyDevice(report_id=1) as dev:
			axes = dev.get_available_axes()
			nof_buttons = dev.get_nof_buttons()
			nof_dhats = dev.get_nof_discrete_hats()
			nof_chats = dev.get_nof_continuous_hats()
			while input('continue to setup?> '):
				input_type = get_option('axis', 'button', 'dhat', 'chat')
				if input_type:
					dev.reset_buttons()
					dev.reset_hats()
					dev.reset()
					if input_type == 'axis':
						axis = get_option(*axes)
						if axis:
							value = get_option(*range(0x1, 0x8000 + 1))
							if value:
								fix_keybinding(dev.set_axis, axis, value)
					elif input_type == 'button':
						button_no = get_option(*range(1, nof_buttons + 1))
						if button_no:
							value = get_option(True, False)
							if value:
								fix_keybinding(dev.set_button, button_no, value)
					elif input_type == 'dhat':
						dhat = get_option(*range(1, nof_dhats + 1))
						if dhat:
							value = get_option(*list(wrap_vjoy.VJoyDevice.DiscreteHatDirection))
							if value:
								fix_keybinding(dev.set_discrete_hat, dhat, value)
					elif input_type == 'chat':
						chat = get_option(*range(1, nof_chats + 1))
						if chat:
							value = get_option(*range(-1, 35999 + 1))
							if value:
								fix_keybinding(dev.set_continuous_hat, chat, value)


@utils_logging.log_call
def select_window():
	while input('position cursor over window> '):
		handles = window_finder.get_window_handles_from_cursor_position()
		for handle in handles:
			window_info = window_finder.window_information(handle)
			while input('show window?> '):
				try:
					SHOTS = screenshot.get_screenshots((handle, ))
					for shot in SHOTS:
						screenshot.show_screenshot(shot)
				except Exception as e:
					logging.warning(e)
			if input(f'choose window {window_info}?> '):
				return handle


if __name__ == "__main__":
	keybinder = KeyBinder()
	keybinder.setup_controls()
	logging.info(keybinder.keybindings)
	handle = None
	while handle is None:
		handle = select_window()
