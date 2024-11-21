import ctypes
import ctypes.wintypes


class INTERNET_PER_CONN_OPTION(ctypes.Structure):
    class Value(ctypes.Union):
        _fields_ = [
            ('dwValue', ctypes.wintypes.DWORD),
            ('pszValue', ctypes.wintypes.LPWSTR),
            ('ftValue', ctypes.wintypes.FILETIME),
        ]

    _fields_ = [
        ('dwOption', ctypes.wintypes.DWORD),
        ('Value', Value),
    ]


class INTERNET_PER_CONN_OPTION_LIST(ctypes.Structure):
    _fields_ = [
        ('dwSize', ctypes.wintypes.DWORD),
        ('pszConnection', ctypes.wintypes.LPWSTR),
        ('dwOptionCount', ctypes.wintypes.DWORD),
        ('dwOptionError', ctypes.wintypes.DWORD),
        ('pOptions', ctypes.POINTER(INTERNET_PER_CONN_OPTION)),
    ]

