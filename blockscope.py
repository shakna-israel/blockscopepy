import ctypes
try:
	from types import DictProxyType as MappingProxyType
except:
	from types import MappingProxyType
from types import MethodType
from contextlib import contextmanager

#
# Credit to Armin Ronacher for most of the work
# on working out how to monkey-patch builtins.
#

if hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
	_Py_ssize_t = ctypes.c_int64
else:
	_Py_ssize_t = ctypes.c_int

class _PyObject(ctypes.Structure):
	pass
_PyObject._fields_ = [
	('ob_refcnt', _Py_ssize_t),
	('ob_type', ctypes.POINTER(_PyObject))
]

if object.__basicsize__ != ctypes.sizeof(_PyObject):
	class _PyObject(ctypes.Structure):
		pass
	_PyObject._fields_ = [
		('_ob_next', ctypes.POINTER(_PyObject)),
		('_ob_prev', ctypes.POINTER(_PyObject)),
		('ob_refcnt', _Py_ssize_t),
		('ob_type', ctypes.POINTER(_PyObject))
	]

class _DictProxy(_PyObject):
	_fields_ = [('dict', ctypes.POINTER(_PyObject))]

def reveal_dict(proxy):
	if not isinstance(proxy, MappingProxyType):
		raise TypeError('{} expected'.format(MappingProxyType))
	dp = _DictProxy.from_address(id(proxy))
	ns = {}
	ctypes.pythonapi.PyDict_SetItem(ctypes.py_object(ns),
									ctypes.py_object(None),
									dp.dict)
	return ns[None]

def get_class_dict(cls):
	d = getattr(cls, '__dict__', None)
	if d is None:
		raise TypeError('No dictionary found for: {}'.format(cls))
	if isinstance(d, MappingProxyType):
		return reveal_dict(d)
	return d

d = get_class_dict(object)
d['__enter__'] = lambda x: x
d['__exit__'] = lambda x,y,z,w: None
