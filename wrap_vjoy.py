import ctypes
from ctypes import wintypes
import enum
import logging

import utils_logging

#Alternative to vJoy - ViGem ?


class JOYSTICK_POSITION_V2(ctypes.Structure):
	_fields_ = [
		('bDevice', ctypes.c_byte),
		('wThrottle', ctypes.c_long),
		('wRudder', ctypes.c_long),
		('wAileron', ctypes.c_long),
		('wAxisX', ctypes.c_long),
		('wAxisY', ctypes.c_long),
		('wAxisZ', ctypes.c_long),
		('wAxisXRot', ctypes.c_long),
		('wAxisYRot', ctypes.c_long),
		('wAxisZRot', ctypes.c_long),
		('wSlider', ctypes.c_long),
		('wDial', ctypes.c_long),
		('wWheel', ctypes.c_long),
		('wAxisVX', ctypes.c_long),
		('wAxisVY', ctypes.c_long),
		('wAxisVZ', ctypes.c_long),
		('wAxisVBRX', ctypes.c_long),
		('wAxisVRBY', ctypes.c_long),
		('wAxisVRBZ', ctypes.c_long),
		('lButtons', ctypes.c_long),  # 32 buttons: 0x00000001 means button1 is pressed, 0x80000000 -> button32 is pressed
		('bHats', ctypes.wintypes.DWORD),  # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
		('bHatsEx1', ctypes.wintypes.DWORD),  # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
		('bHatsEx2', ctypes.wintypes.DWORD),  # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch
		('bHatsEx3', ctypes.wintypes.DWORD),  # Lower 4 bits: HAT switch or 16-bit of continuous HAT switch LONG lButtonsEx1

		# JOYSTICK_POSITION_V2 Extension
		('lButtonsEx1', ctypes.c_long),  # Buttons 33-64	
		('lButtonsEx2', ctypes.c_long),  # Buttons 65-96
		('lButtonsEx3', ctypes.c_long),  # Buttons 97-128
	]


class VJDStatus(enum.IntEnum):
	VJD_STAT_OWN = 0  #The  vJoy Device is owned by this application.
	VJD_STAT_FREE = 1  #The  vJoy Device is NOT owned by any application (including this one).
	VJD_STAT_BUSY = 2  #The  vJoy Device is owned by another application. It cannot be acquired by this application.
	VJD_STAT_MISS = 3  #The  vJoy Device is missing. It either does not exist or the driver is down.
	VJD_STAT_UNKN = 4  #Unknown


class VJDHIDUsage(enum.IntEnum):
	HID_USAGE_X = 0x30
	HID_USAGE_Y = 0x31
	HID_USAGE_Z = 0x32
	HID_USAGE_RX = 0x33
	HID_USAGE_RY = 0x34
	HID_USAGE_RZ = 0x35
	HID_USAGE_SL0 = 0x36
	HID_USAGE_SL1 = 0x37
	HID_USAGE_WHL = 0x38
	HID_USAGE_POV = 0x39


class VJoyInterface:
	dll = ctypes.cdll.LoadLibrary(r"C:\Program Files\vJoy\x64\vJoyInterface.dll")

	@staticmethod
	#	VJOYINTERFACE_API SHORT __cdecl GetvJoyVersion(void);
	@utils_logging.log_call
	def GetvJoyVersion():
		function = VJoyInterface.dll.GetvJoyVersion
		function.restype = ctypes.wintypes.SHORT
		return function(None)

	@staticmethod
	#	VJOYINTERFACE_API PVOID	__cdecl	GetvJoyProductString(void);
	@utils_logging.log_call
	def GetvJoyProductString():
		function = VJoyInterface.dll.GetvJoyProductString
		function.restype = ctypes.c_wchar_p
		result = function(None)
		return str(result)

	@staticmethod
	#	VJOYINTERFACE_API PVOID	__cdecl	GetvJoyManufacturerString(void);
	@utils_logging.log_call
	def GetvJoyManufacturerString():
		function = VJoyInterface.dll.GetvJoyManufacturerString
		function.restype = ctypes.c_wchar_p
		result = function(None)
		return str(result)

	@staticmethod
	#	VJOYINTERFACE_API PVOID	__cdecl	GetvJoySerialNumberString(void);
	@utils_logging.log_call
	def GetvJoySerialNumberString():
		function = VJoyInterface.dll.GetvJoySerialNumberString
		function.restype = ctypes.c_wchar_p
		result = function(None)
		return str(result)

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl vJoyEnabled(void);
	@utils_logging.log_call
	def vJoyEnabled():
		function = VJoyInterface.dll.vJoyEnabled
		function.restype = ctypes.wintypes.BOOL
		return function(None)

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl	DriverMatch(WORD * DllVer, WORD * DrvVer);
	@utils_logging.log_call
	def DriverMatch():
		function = VJoyInterface.dll.DriverMatch
		function.restype = ctypes.wintypes.BOOL
		DllVer = ctypes.wintypes.WORD()
		DrvVer = ctypes.wintypes.WORD()
		result = function(ctypes.byref(DllVer), ctypes.byref(DrvVer))
		return result, DllVer, DrvVer

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl	GetvJoyMaxDevices(int * n);	// What is the maximum possible number of vJoy devices
	@utils_logging.log_call
	def GetvJoyMaxDevices():
		function = VJoyInterface.dll.GetvJoyMaxDevices
		function.restype = ctypes.wintypes.BOOL
		n = ctypes.c_int()
		result = function(ctypes.byref(n))
		return result, n

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl	GetNumberExistingVJD(int * n);	// What is the number of vJoy devices currently enabled
	@utils_logging.log_call
	def GetNumberExistingVJD():
		function = VJoyInterface.dll.GetNumberExistingVJD
		function.restype = ctypes.wintypes.BOOL
		n = ctypes.c_int()
		result = function(ctypes.byref(n))
		return result, n

	#
	#
	#	/////	vJoy Device properties

	@staticmethod
	#	VJOYINTERFACE_API int	__cdecl  GetVJDButtonNumber(UINT rID);	// Get the number of buttons defined in the specified VDJ
	@utils_logging.log_call
	def GetVJDButtonNumber(rID):
		return VJoyInterface.dll.GetVJDButtonNumber(ctypes.wintypes.UINT(rID))

	@staticmethod
	#	VJOYINTERFACE_API int	__cdecl  GetVJDDiscPovNumber(UINT rID);	// Get the number of descrete-type POV hats defined in the specified VDJ
	@utils_logging.log_call
	def GetVJDDiscPovNumber(rID):
		return VJoyInterface.dll.GetVJDDiscPovNumber(ctypes.wintypes.UINT(rID))

	@staticmethod
	#	VJOYINTERFACE_API int	__cdecl  GetVJDContPovNumber(UINT rID);	// Get the number of descrete-type POV hats defined in the specified VDJ
	@utils_logging.log_call
	def GetVJDContPovNumber(rID):
		return VJoyInterface.dll.GetVJDContPovNumber(ctypes.wintypes.UINT(rID))

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl  GetVJDAxisExist(UINT rID, UINT Axis); // Test if given axis defined in the specified VDJ
	@utils_logging.log_call
	def GetVJDAxisExist(rID, Axis):
		function = VJoyInterface.dll.GetVJDAxisExist
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID), ctypes.wintypes.UINT(Axis))
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl  GetVJDAxisMax(UINT rID, UINT Axis, LONG * Max); // Get logical Maximum value for a given axis defined in the specified VDJ
	@utils_logging.log_call
	def GetVJDAxisMax(rID, Axis):
		function = VJoyInterface.dll.GetVJDAxisMax
		function.restype = ctypes.wintypes.BOOL
		Max = ctypes.wintypes.LONG()
		result = function(ctypes.wintypes.UINT(rID), ctypes.wintypes.UINT(Axis), ctypes.byref(Max))
		return result, Max

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl  GetVJDAxisMin(UINT rID, UINT Axis, LONG * Min); // Get logical Minimum value for a given axis defined in the specified VDJ
	@utils_logging.log_call
	def GetVJDAxisMin(rID, Axis):
		function = VJoyInterface.dll.GetVJDAxisMin
		function.restype = ctypes.wintypes.BOOL
		Min = ctypes.wintypes.LONG()
		result = function(ctypes.wintypes.UINT(rID), ctypes.wintypes.UINT(Axis), ctypes.byref(Min))
		return result, Min

	@staticmethod
	#	VJOYINTERFACE_API enum VjdStat	__cdecl	GetVJDStatus(UINT rID);			// Get the status of the specified vJoy Device.
	@utils_logging.log_call
	def GetVJDStatus(rID):
		function = VJoyInterface.dll.GetVJDStatus
		result = function(ctypes.wintypes.UINT(rID))
		return VJDStatus(result)

	#	// Added in 2.1.6

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl	isVJDExists(UINT rID);					// TRUE if the specified vJoy Device exists
	@utils_logging.log_call
	def isVJDExists(rID):
		function = VJoyInterface.dll.isVJDExists
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID))
		return result

	#	// Added in 2.1.8

	@staticmethod
	#	VJOYINTERFACE_API int	__cdecl	GetOwnerPid(UINT rID);					// Reurn owner's Process ID if the specified vJoy Device exists
	@utils_logging.log_call
	def GetOwnerPid(rID):
		function = VJoyInterface.dll.GetOwnerPid
		function.restype = ctypes.c_int
		result = function(ctypes.wintypes.UINT(rID))
		return result

	#
	#
	#	/////	Write access to vJoy Device - Basic

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	AcquireVJD(UINT rID);				// Acquire the specified vJoy Device.
	@utils_logging.log_call
	def AcquireVJD(rID):
		function = VJoyInterface.dll.AcquireVJD
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID))
		return result

	@staticmethod
	#	VJOYINTERFACE_API VOID		__cdecl	RelinquishVJD(UINT rID);			// Relinquish the specified vJoy Device.
	@utils_logging.log_call
	def RelinquishVJD(rID):
		function = VJoyInterface.dll.RelinquishVJD
		function.restype = None
		result = function(ctypes.wintypes.UINT(rID))
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	UpdateVJD(UINT rID, PVOID pData);	// Update the position data of the specified vJoy Device.
	@utils_logging.log_call
	def UpdateVJD(rID, Data: JOYSTICK_POSITION_V2):
		function = VJoyInterface.dll.UpdateVJD
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID), ctypes.byref(Data))
		return result

	#
	#	/////	Write access to vJoy Device - Modifyiers
	#	// This group of functions modify the current value of the position data
	#	// They replace the need to create a structure of position data then call UpdateVJD
	#
	#	//// Reset functions

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	ResetVJD(UINT rID);			// Reset all controls to predefined values in the specified VDJ
	@utils_logging.log_call
	def ResetVJD(rID):
		function = VJoyInterface.dll.ResetVJD
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID))
		return result

	@staticmethod
	#	VJOYINTERFACE_API VOID		__cdecl	ResetAll(void);				// Reset all controls to predefined values in all VDJ
	@utils_logging.log_call
	def ResetAll():
		function = VJoyInterface.dll.ResetAll
		function.restype = None
		result = function()
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	ResetButtons(UINT rID);		// Reset all buttons (To 0) in the specified VDJ
	@utils_logging.log_call
	def ResetButtons(rID):
		function = VJoyInterface.dll.ResetButtons
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID))
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	ResetPovs(UINT rID);		// Reset all POV Switches (To -1) in the specified VDJ
	@utils_logging.log_call
	def ResetPovs(rID):
		function = VJoyInterface.dll.ResetPovs
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID))
		return result

	#
	#	// Write data

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	SetAxis(LONG Value, UINT rID, UINT Axis);		// Write Value to a given axis defined in the specified VDJ
	@utils_logging.log_call
	def SetAxis(Value, rID, Axis):
		function = VJoyInterface.dll.SetAxis
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.LONG(Value), ctypes.wintypes.UINT(rID), ctypes.wintypes.UINT(Axis))
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	SetBtn(BOOL Value, UINT rID, UCHAR nBtn);		// Write Value to a given button defined in the specified VDJ
	@utils_logging.log_call
	def SetBtn(Value, rID, nBtn):
		function = VJoyInterface.dll.SetBtn
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.BOOL(Value), ctypes.wintypes.UINT(rID), ctypes.c_ubyte(nBtn))
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	SetDiscPov(int Value, UINT rID, UCHAR nPov);	// Write Value to a given descrete POV defined in the specified VDJ
	@utils_logging.log_call
	def SetDiscPov(Value, rID, nPov):
		function = VJoyInterface.dll.SetDiscPov
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.INT(Value), ctypes.wintypes.UINT(rID), ctypes.c_ubyte(nPov))
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	SetContPov(DWORD Value, UINT rID, UCHAR nPov);	// Write Value to a given continuous POV defined in the specified VDJ
	@utils_logging.log_call
	def SetContPov(Value, rID, nPov):
		function = VJoyInterface.dll.SetContPov
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.DWORD(Value), ctypes.wintypes.UINT(rID), ctypes.c_ubyte(nPov))
		return result


class VJoyDevice:
	class DiscreteHatDirection(enum.Enum):
		NEUTRAL = -1
		NORTH = 0
		EAST = 1
		SOUTH = 2
		WEST = 3

	@utils_logging.log_call
	def __init__(self, report_id=1):
		self.rID = report_id

	@utils_logging.log_call
	def __enter__(self):
		"""
		Enter the runtime context related to this object. The with statement will bind this method’s return value to the target(s) specified in the as clause of the statement, if any.
		"""
		if VJoyInterface.vJoyEnabled():
			logging.info(
				f"vJoy version:{VJoyInterface.GetvJoyVersion()}\nVendor:{VJoyInterface.GetvJoyManufacturerString()}\nProduct:{VJoyInterface.GetvJoyProductString()}\nSerial number:{VJoyInterface.GetvJoySerialNumberString()}"
			)
			ok, dll_ver, drv_ver = VJoyInterface.DriverMatch()
			if ok:
				vjdExists = VJoyInterface.isVJDExists(self.rID)
				if vjdExists:
					status = VJoyInterface.GetVJDStatus(self.rID)
					owner_pid = VJoyInterface.GetOwnerPid(self.rID)
					logging.debug(f"status={status} pid={owner_pid}.")
					if status == VJDStatus.VJD_STAT_OWN:
						pass
					elif status == VJDStatus.VJD_STAT_FREE:
						if not VJoyInterface.AcquireVJD(self.rID):
							raise RuntimeError(f"Failed to acquire vJoy device number {self.rID}.")
					elif status == VJDStatus.VJD_STAT_BUSY:
						raise RuntimeError(f"{status}: pid {owner_pid} owns the vJoy device number {self.rID}.")
					else:
						raise RuntimeError(status)
					return self
				else:
					raise RuntimeError(
						f"vjoy device {self.rID} is not configured and enabled. Possible causes: Device does not exist, device is disabled, driver is not installed, ..."
					)
			else:
				raise RuntimeError(f"vJoyInterface DLL (version {dll_ver}) does not match vJoy Driver (version {drv:ver})")
		else:
			raise RuntimeError("vJoy not enabled.")

	@utils_logging.log_call
	def get_available_axes(self):
		return {hid_used for hid_used in list(VJDHIDUsage) if VJoyInterface.GetVJDAxisExist(self.rID, hid_used)}

	@utils_logging.log_call
	def get_nof_buttons(self):
		return VJoyInterface.GetVJDButtonNumber(self.rID)

	@utils_logging.log_call
	def get_nof_discrete_hats(self):
		return VJoyInterface.GetVJDDiscPovNumber(self.rID)

	@utils_logging.log_call
	def get_nof_continuous_hats(self):
		return VJoyInterface.GetVJDContPovNumber(self.rID)

	@utils_logging.log_call
	def reset(self):
		return VJoyInterface.ResetVJD(self.rID)

	@utils_logging.log_call
	def reset_buttons(self):
		return VJoyInterface.ResetButtons(self.rID)

	@utils_logging.log_call
	def reset_hats(self):
		return VJoyInterface.ResetPovs(self.rID)

	@utils_logging.log_call
	def set_axis(self, axis: VJDHIDUsage, value):
		axes = self.get_available_axes()
		if axis in axes:
			if (0x1 <= value) and (value <= 0x8000):
				return VJoyInterface.SetAxis(value, self.rID, axis)
			else:
				raise ValueError(f"value is not within bounds: {0x1}=0x1<={value}<=0x8000={0x8000}")
		else:
			raise ValueError(f"axis {axis} is not in available axes ({axes})")

	@utils_logging.log_call
	def set_button(self, button_no, value: bool):
		nof_buttons = self.get_nof_buttons()
		if (1 <= button_no) and (button_no <= nof_buttons):
			if (0 <= value) and (value <= 1):
				return VJoyInterface.SetBtn(value, self.rID, button_no)
			else:
				raise ValueError(f"value is not within bounds: 0<={value}<=1")
		else:
			raise ValueError(f"button_no {button_no} is not within bounds 1<={button_no}<={nof_buttons}")

	@utils_logging.log_call
	def set_discrete_hat(self, hat_no, value):
		nof_discrete_hats = self.get_nof_discrete_hats()
		if (1 <= hat_no) and (hat_no <= nof_discrete_hats):
			if value in list(DiscreteHatDirection):
				return VJoyInterface.SetDiscPov(value, self.rID, hat_no)
			else:
				raise ValueError(f"value {value} should be one of {list(DiscreteHatDirection)}")
		else:
			raise ValueError(f"discrete hat no {hat_no} is not within bounds 1<={hat_no}<={nof_discrete_hats}")

	@utils_logging.log_call
	def set_continuous_hat(self, hat_no, value):
		"""[summary]

		:param hat_no: identity number of the continuous hat / POV 
		:param value: can be in the range: -1 to 35999. It is measured in units of 0.01 degrees. -1 means Neutral (Nothing pressed).
		:raises ValueError: [description]
		:raises ValueError: [description]
		"""

		nof_continuous_hats = self.get_nof_continuous_hats()
		if (1 <= hat_no) and (hat_no <= nof_continuous_hats):
			if -1 <= value and value <= 35999:
				VJoyInterface.SetContPov(value, self.rID, hat_no)
			else:
				raise ValueError(f"value {value} should be in range -1 to 35999")
		else:
			raise ValueError(f"continuous hat no {hat_no} is not within bounds 1<={hat_no}<={nof_continuous_hats}")

	@utils_logging.log_call
	def __exit__(self, exc_type, exc_value, traceback):
		"""
		Exit the runtime context related to this object. The parameters describe the exception that caused the context to be exited. If the context was exited without an exception, all three arguments will be None.
		If an exception is supplied, and the method wishes to suppress the exception (i.e., prevent it from being propagated), it should return a true value. Otherwise, the exception will be processed normally upon exit from this method.
		Note that __exit__() methods should not reraise the passed-in exception; this is the caller’s responsibility.
		"""
		VJoyInterface.RelinquishVJD(self.rID)
		if VJoyInterface.GetVJDStatus(self.rID) is not VJDStatus.VJD_STAT_FREE:
			raise RuntimeError()
		return False
