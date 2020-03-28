

# autocontainer

Python really needed a modern reflection based dependency injection container
that "just works". Alas, welcome to **autocontainer** for python. The dependency injection service contaienr that just works.

## Installation

```bash
pip3 install autocontainer
```

## Usage

It's all about types and hints, but first create the container

```python
from autocontianer import Container

container = Container()
```

### Available Methods

- `get(service: Union[Type, str])`
	Retreives a service

- `has(service: Union[Type, str])`  
	Returns if a service exists

- `singleton(service: Union[Type, Callable[..., Instance]], name?: str)`  
	Adds a service as a singleton into container.
	(Returns the same object on every `get`)

- `factory(service: Union[Type, Callable[..., Instance]], name?: str)`  
	Adds a service as a factory into container.
	(Returns a fresh object on every `get`)

- `instance(service: object, name?: str)`  
	Adds a service as an instance into container.
	(Returns the same object on every `get`, but does not try to instantiate)

- `assembler(service: Union[Type, Callable[..., Instance]], name?: str)`  
	Adds a service such that on every get, the container returns a _bound_ callable
	that produces a fresh object everytime.

- `bind(func: Callable)`  
	Returns a new callable but in which the arguments recognized by the container
	are automatically pushed when calling. (see examples below)

- `inject(func: Callable)`  
	Takes a callable and calls it by injecting all the services it requires
	and then returns the return value.

### Classes & Injection

We'll use singleton as an example.

```python
class A:
    pass

class B:
    def __init__(self, obj_a: A):
        assert isinstance(obj_a, A)

# Order does not matter.
container.singleton(B)
container.singleton(A)

obj_b = container.get(B)
assert isinstance(obj_b, B)
```

### Naming Services

```python
class A:
    pass

container.singleton(A, 'ayy')

obj_a = container.get(A)
obj_b = container.get('ayy')


assert obj_a is obj_b
```

### Other ways to `get`

```python
obj_a = container.get(A)      # <--- Best IDE Support due to type hints.
obj_b = container.get('ayy')
obj_c = container.ayy         # <--- the most concise way.
obj_d = container('ayy')
```

### Builder Functions

You won't always put raw classes into the service container
sometimes, it's necessary to write a function that custom
initializes a class or object.

```python
class A:
    pass

class B:
    def __init__(self):
        self.fruit = 'tomato'

def makeB(obj_a: A) -> B: # Return type MUST be annotated
    b = B()
    b.fruit = 'mango'

    return b

container.singleton(makeB)

obj_b = container(B)

assert obj_b.fruit == 'mango'
```

### Factory

Factories can also take builder function as well as classes.
The container returns a new instance every time.

```python
class A:
    pass

container.factory(A)

aa = container.get(A)
ab = container.get(A)

assert aa is not ab
assert isinstance(aa, A)
assert isinstance(ab, A)
```

### Binding

This is the coolest feature, trust me. Imagine you have a function
that needs both classes out of a container and vanilla arguments
like int and str, this would be a pain to do manually. Unless...

```python
class A:
    pass

class B:
    pass

container.singleton(A)
container.singleton(B)

def crazy_function(a: A, repeating: str, b: B, times: int):
    assert isinstance(a, A)
    assert isinstance(b, B)

    return repeating * time

less_crazy_function = container.bind(crazy_function)

result = less_crazy_function("pew", 3)
assert result == 'pewpewpew'
```

### Injecting

Same as binding but for simpler times.

```python
class A:
    pass

class B:
    pass

container.singleton(A)
container.singleton(B)

def crazy_function(a: A, b: B):
    assert isinstance(a, A)
    assert isinstance(b, B)

    return 'potato'

assert contianer.inject(crazy_function) == 'potato'
```


### Specificity Injector

The container maintains an internal graph of dependencies that allows
it to efficiently push instances of ancestor classes.

```python
class A:
    pass

class B:
    pass

class C(A):
    pass

class D(C, B):
    pass

container.factory(A)
container.singleton(B)
container.factory(C)
container.singleton(D)

obj = container.get(A)
assert isinstance(obj, D)
assert isinstance(obj, A)
```

### Hinting by Name

This is completely valid with the container

```python
class A:
    pass

container.singleton(A, 'apple')

def magic(ap: 'apple'):
    assert isinstance(ap, A)

container.inject(magic)
```

## Running Tests
```bash
python -m unittest discover -s ./
```

## License
MIT. Go crazy.


