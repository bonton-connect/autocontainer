from typing import Type, TypeVar, Any, Callable, Union, List
from inspect import Signature
import inspect
import importlib

ReturnType = TypeVar('ReturnType')
GettingType = TypeVar('GettingType')
ServiceableType = Union[str, Type, Callable, object]


class ServiceResolutionException(Exception):
	pass


class Singleton:
	def __init__(self, injector, service):
		self._obj = None
		self.inject = injector
		self.service = service

	def __call__(self):
		if self._obj is None:
			self._obj = self.inject(self.service)

		return self._obj


class BoundCall:
	def __init__(self, unknowns: List[str], knowns: dict, cal: Callable):
		self._unkowns = unknowns
		self._knowns = knowns
		self._cal = cal

	def __call__(self, *args, **kwargs):
		expected_len = len(self._knowns.items())
		given_len = (len(kwargs.items()) + len(args))

		if given_len != expected_len:
			raise Exception(f'{expected_len} arguments expected, {given_len} given.')

		ordered_args = dict(
			zip(
				self._unkowns[:len(args)],
				args
			)
		)

		params = dict(
			**self._knowns,
			**ordered_args,
			**kwargs
		)

		return self._cal(**params)


def isNative(var) -> bool:
	return isinstance(var, str)	\
		or isinstance(var, list) \
		or isinstance(var, dict) \
		or isinstance(var, int) \
		or isinstance(var, float) \
		or isinstance(var, tuple) \
		or isinstance(var, bool)


def getImportName(cls: Type) -> str:
	return f'{cls.__module__}.{cls.__name__}'


class Container:
	def __init__(self):
		self._graph = {}
		self._named = {}

		self.instance(self, 'container')

	def get(self, service: Union[str, Type[GettingType]], for_obj: Any = None) -> GettingType:
		entry = None

		if isinstance(service, str):
			if service in self._named:
				mapping = self._named[service]

				if isinstance(mapping, str):
					entry = self._graph[mapping]
				else:
					return mapping.init()

			elif service in self._graph:
				entry = self._graph[service]

			else:
				raise ServiceResolutionException(f'{service} does not exist.')

		elif inspect.isclass(service):
			key = getImportName(service)

			if key in self._graph:
				entry = self._graph[key]
			else:
				raise ServiceResolutionException(f'{key} does not exist.')

		else:
			raise ServiceResolutionException(f'{service} does not exist.')

		while 'subs' in entry and len(entry['subs']) == 1:
			entry = self._graph[list(entry['subs'])[0]]

		if 'subs' in entry and len(entry['subs']) > 1:
			alternatives = ", ".join(list(entry['subs']))
			raise ServiceResolutionException(f'Too many candidates for {service}, like: {alternatives}')

		return entry['init']()

	def _addEntry(self, service: ServiceableType, mode: str, name: str = False):
		cls = None

		if isinstance(service, str):
			mod = inspect.getmodule(inspect.stack()[1].frame).__name__
			package: str = importlib.import_module(('.' if service[0] is '.' else '') + service, mod)
			module = importlib.import_module(package)

			cls = getattr(module, package.split('.')[-1])
			service = cls

		elif inspect.isclass(service):
			cls = service

		elif inspect.isfunction(service):
			return_type = inspect.signature(service).return_annotation

			if return_type is Signature.empty:
				assert name, 'Must include service name as there is no return type annotation.'

				self._named[name] = dict(
					name=name,
					init=lambda: service
				)
			else:
				cls = return_type

		elif isinstance(service, object) and not isNative(service):
			cls = service.__class__

		key = getImportName(cls)
		entry = dict(
			name=key,
			subs=set()
		)

		self._graph[key] = entry

		if name:
			self._named[name] = key

		init: Callable = None

		if mode == 'singleton':
			init = Singleton(self.inject, service)

		elif mode == 'factory':
			init = lambda: self.inject(service)

		elif mode == 'assembler':
			init = lambda: self.bind(service)

		elif mode == 'instance':
			init = lambda: service

		entry['init'] = init

		self._updateGraph(cls)

	def _updateGraph(self, cls: Type):
		if cls is object:
			return

		key = getImportName(cls)
		bases = cls.__bases__

		for base in bases:
			if base is cls:
				continue

			base_key = getImportName(base)

			if base_key not in self._graph:
				self._graph[base_key] = dict(
					name=base_key,
					subs=set()
				)

			self._graph[base_key]['subs'].add(key)
			self._updateGraph(base)

	def singleton(self, service: ServiceableType, name: str = False) -> None:
		self._addEntry(service, 'singleton', name)

	def factory(self, service: ServiceableType, name: str = False) -> None:
		self._addEntry(service, 'factory', name)

	def assembler(self, service: ServiceableType, name: str = False) -> None:
		self._addEntry(service, 'assembler', name)

	def instance(self, service: Any, name: str = False) -> None:
		if isNative(service):
			assert name, 'Name must be specified as it is not an instance.'

			self._named[name] = dict(
				name=name,
				init=lambda: service
			)

		elif isinstance(service, object):
			self._addEntry(service, 'instance', name)

	def has(self, service: ServiceableType) -> bool:
		try:
			return not not self.get(service)
		except ServiceResolutionException:
			return False

	def bind(self, cal: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
		calling_args = {}
		params = inspect.signature(cal).parameters
		unknown_params = []

		for param in params:
			annotation = params[param].annotation

			if annotation not in [int, str, bool, float, list, dict, tuple] and self.has(annotation):
				calling_args[param] = self.get(annotation, cal)
			else:
				unknown_params.append(param)

		return BoundCall(unknown_params, calling_args, cal)

	def inject(self, cal: Callable[..., ReturnType]) -> ReturnType:
		calling_args = {}
		params = inspect.signature(cal).parameters

		for param in params:
			calling_args[param] = self.get(params[param].annotation, cal)

		return cal(**calling_args)

	def __contains__(self, item):
		return self.has(item)

	def __getattr__(self, name: str) -> Any:
		if name in self.__dict__:
			return self.__dict__[name]

		return self.get(name)

	def __call__(self, item):
		return self.get(item)

