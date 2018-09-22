import ctypes
import enum
import logging

logging.basicConfig(format="[%(asctime)s][%(relativeCreated)07dms][%(levelname)s][%(processName)s:%(threadName)s:%(name)s.%(funcName)s]:\t%(message)s", level=logging.DEBUG)


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


class VJDStatus(enum.Enum):
	VJD_STAT_OWN = 0,  #The  vJoy Device is owned by this application.
	VJD_STAT_FREE = 1,  #The  vJoy Device is NOT owned by any application (including this one).
	VJD_STAT_BUSY = 2,  #The  vJoy Device is owned by another application. It cannot be acquired by this application.
	VJD_STAT_MISS = 3,  #The  vJoy Device is missing. It either does not exist or the driver is down.
	VJD_STAT_UNKN = 4,  #Unknown


class VJDHIDUsage(enum.Enum):
	HID_USAGE_X = 0x30,
	HID_USAGE_Y = 0x31,
	HID_USAGE_Z = 0x32,
	HID_USAGE_RX = 0x33,
	HID_USAGE_RY = 0x34,
	HID_USAGE_RZ = 0x35,
	HID_USAGE_SL0 = 0x36,
	HID_USAGE_SL1 = 0x37,
	HID_USAGE_WHL = 0x38,
	HID_USAGE_POV = 0x39,


class VJoyInterface:
	dll = ctypes.cdll.LoadLibrary(r"C:\Program Files\vJoy\x64\vJoyInterface.dll")

	@staticmethod
	#	VJOYINTERFACE_API SHORT __cdecl GetvJoyVersion(void);
	def GetvJoyVersion():
		function = VJoyInterface.dll.GetvJoyVersion
		function.restype = ctypes.wintypes.SHORT
		return function(None)

	@staticmethod
	#	VJOYINTERFACE_API PVOID	__cdecl	GetvJoyProductString(void);
	def GetvJoyProductString():
		function = VJoyInterface.dll.GetvJoyProductString
		function.restype = ctypes.c_wchar_p
		result = function(None)
		return str(result)

	@staticmethod
	#	VJOYINTERFACE_API PVOID	__cdecl	GetvJoyManufacturerString(void);
	def GetvJoyManufacturerString():
		function = VJoyInterface.dll.GetvJoyManufacturerString
		function.restype = ctypes.c_wchar_p
		result = function(None)
		return str(result)

	@staticmethod
	#	VJOYINTERFACE_API PVOID	__cdecl	GetvJoySerialNumberString(void);
	def GetvJoySerialNumberString():
		function = VJoyInterface.dll.GetvJoySerialNumberString
		function.restype = ctypes.c_wchar_p
		result = function(None)
		return str(result)

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl vJoyEnabled(void);
	def vJoyEnabled():
		function = VJoyInterface.dll.vJoyEnabled
		function.restype = ctypes.wintypes.BOOL
		return function(None)

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl	DriverMatch(WORD * DllVer, WORD * DrvVer);
	def DriverMatch():
		function = VJoyInterface.dll.DriverMatch
		function.restype = ctypes.wintypes.BOOL
		DllVer = ctypes.wintypes.WORD
		DrvVer = ctypes.wintypes.WORD
		result = function(ctypes.byref(DllVer), ctypes.byref(DrvVer))
		return result, DllVer, DrvVer

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl	GetvJoyMaxDevices(int * n);	// What is the maximum possible number of vJoy devices
	def GetvJoyMaxDevices():
		function = VJoyInterface.dll.GetvJoyMaxDevices
		function.restype = ctypes.wintypes.BOOL
		n = ctypes.c_int
		result = function(byref(n))
		return result, n

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl	GetNumberExistingVJD(int * n);	// What is the number of vJoy devices currently enabled
	def GetNumberExistingVJD():
		function = VJoyInterface.dll.GetNumberExistingVJD
		function.restype = ctypes.wintypes.BOOL
		n = ctypes.c_int
		result = function(byref(n))
		return result, n
#
#
#	/////	vJoy Device properties

	@staticmethod
	#	VJOYINTERFACE_API int	__cdecl  GetVJDButtonNumber(UINT rID);	// Get the number of buttons defined in the specified VDJ
	def GetVJDButtonNumber(rID):
		return VJoyInterface.dll.GetVJDButtonNumber(ctypes.wintypes.UINT(rID))

	@staticmethod
	#	VJOYINTERFACE_API int	__cdecl  GetVJDDiscPovNumber(UINT rID);	// Get the number of descrete-type POV hats defined in the specified VDJ
	def GetVJDDiscPovNumber(rID):
		return VJoyInterface.dll.GetVJDDiscPovNumber(ctypes.wintypes.UINT(rID))

	@staticmethod
	#	VJOYINTERFACE_API int	__cdecl  GetVJDContPovNumber(UINT rID);	// Get the number of descrete-type POV hats defined in the specified VDJ
	def GetVJDContPovNumber(rID):
		return VJoyInterface.dll.GetVJDContPovNumber(ctypes.wintypes.UINT(rID))

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl  GetVJDAxisExist(UINT rID, UINT Axis); // Test if given axis defined in the specified VDJ
	def GetVJDAxisExist(rID, Axis):
		function = VJoyInterface.dll.GetVJDAxisExist
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID), ctypes.wintypes.UINT(Axis))
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl  GetVJDAxisMax(UINT rID, UINT Axis, LONG * Max); // Get logical Maximum value for a given axis defined in the specified VDJ
	def GetVJDAxisMax(rID, Axis):
		function = VJoyInterface.dll.GetVJDAxisMax
		function.restype = ctypes.wintypes.BOOL
		Max = ctypes.wintypes.LONG
		result = function(ctypes.wintypes.UINT(rID), ctypes.wintypes.UINT(Axis), ctypes.byref(Max))
		return result, Max

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl  GetVJDAxisMin(UINT rID, UINT Axis, LONG * Min); // Get logical Minimum value for a given axis defined in the specified VDJ
	def GetVJDAxisMin(rID, Axis):
		function = VJoyInterface.dll.GetVJDAxisMin
		function.restype = ctypes.wintypes.BOOL
		Min = ctypes.wintypes.LONG
		result = function(ctypes.wintypes.UINT(rID), ctypes.wintypes.UINT(Axis), ctypes.byref(Min))
		return result, Min
#	VJOYINTERFACE_API enum VjdStat	__cdecl	GetVJDStatus(UINT rID);			// Get the status of the specified vJoy Device.

	def GetVJDStatus(rID):
		function = VJoyInterface.dll.GetVJDAxisMin
		result = function(ctypes.wintypes.UINT(rID))
		return VJDStatus(result)

#	// Added in 2.1.6

	@staticmethod
	#	VJOYINTERFACE_API BOOL	__cdecl	isVJDExists(UINT rID);					// TRUE if the specified vJoy Device exists
	def isVJDExists(rID):
		function = VJoyInterface.dll.isVJDExists
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID))
		return result
#	// Added in 2.1.8

	@staticmethod
	#	VJOYINTERFACE_API int	__cdecl	GetOwnerPid(UINT rID);					// Reurn owner's Process ID if the specified vJoy Device exists
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
	def AcquireVJD(rID):
		function = VJoyInterface.dll.AcquireVJD
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID))
		return result

	@staticmethod
	#	VJOYINTERFACE_API VOID		__cdecl	RelinquishVJD(UINT rID);			// Relinquish the specified vJoy Device.
	def RelinquishVJD(rID):
		function = VJoyInterface.dll.RelinquishVJD
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID))
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	UpdateVJD(UINT rID, PVOID pData);	// Update the position data of the specified vJoy Device.
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
	def ResetVJD(rID):
		function = VJoyInterface.dll.ResetVJD
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID))
		return result

	@staticmethod
	#	VJOYINTERFACE_API VOID		__cdecl	ResetAll(void);				// Reset all controls to predefined values in all VDJ
	def ResetAll():
		function = VJoyInterface.dll.ResetAll
		function.restype = None
		result = function()
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	ResetButtons(UINT rID);		// Reset all buttons (To 0) in the specified VDJ
	def ResetButtons(rID):
		function = VJoyInterface.dll.ResetButtons
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID))
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	ResetPovs(UINT rID);		// Reset all POV Switches (To -1) in the specified VDJ
	def ResetPovs(rID):
		function = VJoyInterface.dll.ResetPovs
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.UINT(rID))
		return result


#
#	// Write data

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	SetAxis(LONG Value, UINT rID, UINT Axis);		// Write Value to a given axis defined in the specified VDJ
	def SetAxis(Value, rID, Axis):
		function = VJoyInterface.dll.SetAxis
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.LONG(Value), ctypes.wintypes.UINT(rID), ctypes.wintypes.UINT(Axis))
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	SetBtn(BOOL Value, UINT rID, UCHAR nBtn);		// Write Value to a given button defined in the specified VDJ
	def SetBtn(Value, rID, nBtn):
		function = VJoyInterface.dll.SetAxis
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.BOOL(Value), ctypes.wintypes.UINT(rID), ctypes.c_ubyte(Axis))
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	SetDiscPov(int Value, UINT rID, UCHAR nPov);	// Write Value to a given descrete POV defined in the specified VDJ
	def SetDiscPov(Value, rID, nPov):
		function = VJoyInterface.dll.SetDiscPov
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.INT(Value), ctypes.wintypes.UINT(rID), ctypes.c_ubyte(nPov))
		return result

	@staticmethod
	#	VJOYINTERFACE_API BOOL		__cdecl	SetContPov(DWORD Value, UINT rID, UCHAR nPov);	// Write Value to a given continuous POV defined in the specified VDJ
	def SetDiscPov(Value, rID, nPov):
		function = VJoyInterface.dll.SetDiscPov
		function.restype = ctypes.wintypes.BOOL
		result = function(ctypes.wintypes.DWORD(Value), ctypes.wintypes.UINT(rID), ctypes.c_ubyte(nPov))
		return result


class VJoyDevice:
	def __init__(self, report_id=1):
		self.rID = report_id
		self.available_axes = None
		self.nof_buttons = None

	def __enter__(self):
		"""
		Enter the runtime context related to this object. The with statement will bind this method’s return value to the target(s) specified in the as clause of the statement, if any.
		"""
		if VJoyInterface.vJoyEnabled():
			logging.info("\nVendor:{0}\nProduct:{1}\nVersion Number:{2}".format(VJoyInterface.GetvJoyManufacturerString(), VJoyInterface.GetvJoyProductString(), VJoyInterface.GetvJoySerialNumberString()))
			ok, dll_ver, drv_ver = VJoyInterface.DriverMatch()
			if ok:
				logging.info("\nvJoy dll version:{0}\nvJoy driver version:{1}".format(dll_ver, drv_ver))
				status = VJoyInterface.GetVJDStatus(self.rID)
				if status == VJDStatus.VJD_STAT_OWN:
					pass
				elif status == VJDStatus.VJD_STAT_FREE:
					if not VJoyInterface.AcquireVJD(self.rID):
						raise RunTimeError("Failed to acquire vJoy device number {0}.".format(self.rID))
				else:
					raise RuntimeError(status)
			else:
				raise RuntimeError("vJoyInterface DLL (version {0}) does not match vJoy Driver (version {0})".format(dll_ver, drv_ver))
		else:
			raise RuntimeError("vJoy not enabled.")

	def get_available_axes(self):
		return {hid_used for hid_used in list(VJDHIDUsage) if VJoyInterface.GetVJDAxisExist(self.rID, hid_used.value)}

	def get_nof_buttons(self):
		return VJoyInterface.GetVJDButtonNumber(self.rID)

	def get_nof_discrete_hats(self):
		return VJoyInterface.GetVJDDiscPovNumber(self.rID)

	def get_nof_continuous_hats(self):
		return VJoyInterface.GetVJDContPovNumber(self.rID)

	def __exit__(self, exc_type, exc_value, traceback):
		"""
		Exit the runtime context related to this object. The parameters describe the exception that caused the context to be exited. If the context was exited without an exception, all three arguments will be None.
		If an exception is supplied, and the method wishes to suppress the exception (i.e., prevent it from being propagated), it should return a true value. Otherwise, the exception will be processed normally upon exit from this method.
		Note that __exit__() methods should not reraise the passed-in exception; this is the caller’s responsibility.
		"""
		if not VJoyInterface.RelinquishVJD(self.rID):
			raise RuntimeError()
		return False
