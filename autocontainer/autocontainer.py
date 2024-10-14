from typing import Type, TypeVar, Any, Callable, Union, List, NamedTuple, Set, Literal
from inspect import Signature
import inspect

ReturnType = TypeVar('ReturnType')
GettingType = TypeVar('GettingType')
ServiceableType = Union[str, Type, Callable, object]

class NamedEntry(NamedTuple):
	name: str
	init: Union[Callable, None]

class GraphEntry(NamedTuple):
	name: str
	subs: Set
	init: Union[Callable, None]

Mode = Union[
	Literal['singleton'],
	Literal['assembler'],
	Literal['singleton'],
	Literal['factory'],
	Literal['instance'],
]


class ServiceResolutionException(Exception):
	pass


class Singleton:
	def __init__(self, injector, service, cls):
		self._obj = None
		self.inject = injector
		self.service = service
		self.cls = cls

	def __call__(self):
		if self._obj is None:
			self._obj = self.inject(self.service)
			assert isinstance(self._obj, self.cls)

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


def is_native(var) -> bool:
	return isinstance(var, str)	\
		or isinstance(var, list) \
		or isinstance(var, dict) \
		or isinstance(var, int) \
		or isinstance(var, float) \
		or isinstance(var, tuple) \
		or isinstance(var, bool)


def get_import_name(cls: Type) -> str:
	return f'{cls.__module__}.{cls.__name__}'

class Container:
	def __init__(self):
		self._graph: dict[str, GraphEntry] = {}
		self._named: dict[str, Union[NamedEntry, str]] = {}

		self.instance(self, 'container')

	def get(self, service: Union[str, Type[GettingType]]) -> GettingType:
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
			key = get_import_name(service)

			if key in self._graph:
				entry = self._graph[key]
			else:
				raise ServiceResolutionException(f'{key} does not exist.')

		else:
			raise ServiceResolutionException(f'{service} does not exist.')

		while 'subs' in entry and len(entry.subs) == 1:
			entry = self._graph[list(entry.subs)[0]]

		if 'subs' in entry and len(entry.subs) > 1:
			alternatives = ", ".join(list(entry.subs))
			raise ServiceResolutionException(f'Too many candidates for {service}, like: {alternatives}')

		return entry.init()

	def _add_entry(self, service: ServiceableType, mode: Mode, name: Union[str, False] = False):
		cls = None

		if inspect.isclass(service):
			cls = service

		elif inspect.isfunction(service):
			return_type = inspect.signature(service).return_annotation

			if return_type is Signature.empty:
				assert name, 'Must include service name as there is no return type annotation.'

				self._named[name] = NamedEntry(
					name=name,
					init=lambda: service
				)
			else:
				cls = return_type

		elif isinstance(service, object) and not is_native(service):
			cls = service.__class__

		key = get_import_name(cls)

		entry = GraphEntry(
			name=key,
			subs=set(),
			init=None
		)

		self._graph[key] = entry

		if name:
			self._named[name] = key

		init: Union[Callable, None] = None

		if mode == 'singleton':
			init = Singleton(self.inject, service, cls)

		elif mode == 'factory':
			def maker():
				obj = self.inject(service)
				assert isinstance(obj, cls)
				return obj

			init = maker

		elif mode == 'assembler':
			init = lambda: self.bind(service)

		elif mode == 'instance':
			init = lambda: service

		entry.init = init

		self._update_graph(cls)

	def _update_graph(self, cls: Type):
		if cls is object:
			return

		key = get_import_name(cls)
		bases = cls.__bases__

		for base in bases:
			if base is cls:
				continue

			base_key = get_import_name(base)

			if base_key not in self._graph:
				self._graph[base_key] = GraphEntry(
					name=base_key,
					subs=set(),
					init=None
				)

			self._graph[base_key].subs.add(key)
			self._update_graph(base)

	def singleton(self, service: ServiceableType, name: Union[str, False] = False) -> None:
		self._add_entry(service, 'singleton', name)

	def factory(self, service: ServiceableType, name: Union[str, False] = False) -> None:
		self._add_entry(service, 'factory', name)

	def assembler(self, service: ServiceableType, name: Union[str, False] = False) -> None:
		self._add_entry(service, 'assembler', name)

	def instance(self, service: Any, name: Union[str, False] = False) -> None:
		if is_native(service):
			assert name, 'Name must be specified as it is not an instance.'

			self._named[name] = NamedEntry(
				name=name,
				init=lambda: service
			)

		elif isinstance(service, object):
			self._add_entry(service, 'instance', name)

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
				calling_args[param] = self.get(annotation)
			else:
				unknown_params.append(param)

		return BoundCall(unknown_params, calling_args, cal)

	def inject(self, cal: Callable[..., ReturnType]) -> ReturnType:
		calling_args = {}
		params = inspect.signature(cal).parameters

		for param in params:
			calling_args[param] = self.get(params[param].annotation)

		return cal(**calling_args)

	def __contains__(self, item: Union[str, Type[GettingType]]):
		return self.has(item)

	def __getattr__(self, item: Union[str, Type[GettingType]]) -> Any:
		if isinstance(item, str) and item in self.__dict__:
			return self.__dict__[item]

		return self.get(item)

	def __call__(self, item: Union[str, Type[GettingType]]):
		return self.get(item)

