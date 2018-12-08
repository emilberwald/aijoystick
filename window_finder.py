"""
The purpose of this module is to help finding window handles.
"""

import platform

if platform.system().lower() == 'windows':
	from window_finder_windows import process_information, window_information, get_window_handles, get_window_handles_from_cursor_position
