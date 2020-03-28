import unittest
from autocontainer.autocontainer import Container


class A:
    pass


class E:
    pass


class F:
    def __init__(self, e: E):
        assert isinstance(e, E)


class TestContainer(unittest.TestCase):
    def setUp(self):
        self.container = Container()

    def test_it_should_return_same_instance(self):
        inst = A()

        self.container.instance(inst, 'apple')

        app_a = self.container.get('apple')
        app_b = self.container.get('apple')
        app_c = self.container.get(A)

        assert app_a is app_b
        assert app_b is app_c
        assert app_c is inst

    def test_it_should_support_getting_instances_by_class(self):
        inst = A()

        self.container.instance(inst)

        app_a = self.container.get(A)
        app_b = self.container.get(A)

        assert app_a is app_b
        assert app_b is inst

    def test_it_should_instantiate_singleton_on_first_get(self):
        shared_state = dict(throw=True)

        class B:
            def __init__(self):
                if shared_state['throw']:
                    raise Exception('Should not be instantiated now.')

        self.container.singleton(B)

        shared_state['throw'] = False

        assert not not self.container.get(B)

    def test_it_should_return_the_same_singleton(self):
        class C:
            pass

        self.container.singleton(C, 'see')

        assert self.container.get('see') is self.container.get('see')

    def test_it_should_support_singleton_builder_functions(self):
        class D:
            pass

        def buildD() -> D:
            return D()

        self.container.singleton(buildD, 'dee')
        assert self.container.get('dee') is self.container.get(D)

    def test_it_should_inject_deps_into_singleton_init(self):
        self.container.singleton(E)
        self.container.singleton(F, 'ef')
        assert self.container.get(F) is self.container.get('ef')

    def test_it_should_inject_deps_into_singleton_builder(self):
        def buildF(e: E, a: A) -> F:
            assert isinstance(e, E)
            assert isinstance(a, A)
            return F(e)

        self.container.singleton(A)
        self.container.singleton(E, 'eee')
        self.container.singleton(buildF, 'ef')

        assert self.container.get(F) is self.container.get('ef')

    def test_it_should_return_different_objs_for_factory(self):
        class G:
            pass

        self.container.factory(G, 'jee')
        assert self.container.get(G) is not self.container.get('jee')

    def test_it_should_support_factory_builder(self):
        class G:
            pass

        def buildG(a: A) -> G:
            assert isinstance(a, A)
            return G()

        self.container.factory(buildG, 'jee')
        self.container.singleton(A)

        assert self.container.get(G) is not self.container.get('jee')

    def test_it_should_push_the_grandchild_class_if_available(self):
        class A:
            pass

        class B(A):
            pass

        class C:
            pass

        class D(B, C):
            pass

        self.container.singleton(B)
        self.container.singleton(D)

        assert isinstance(self.container.get(A), D)
        assert isinstance(self.container.get(C), D)

    def test_it_should_reject_multi_candidate_base_class(self):
        class A:
            pass

        class B(A):
            pass

        class C(A):
            pass

        class D(B, C):
            pass

        self.container.singleton(B)
        self.container.singleton(D)

        self.assertRaises(Exception, lambda: self.container.get(A))

    def test_it_should_inject_known_classes_and_return_value(self):
        class A:
            pass

        class B:
            pass

        def test(a: A, b: B):
            assert isinstance(a, A)
            assert isinstance(b, B)

            return "worked"

        self.container.singleton(A)
        self.container.factory(B)

        assert self.container.inject(test) == "worked"

    def test_it_should_bind_only_known_types(self):
        class A:
            pass

        class B:
            pass

        def test(a: A, var: str, b: B, tomato: 5):
            assert isinstance(a, A)
            assert isinstance(b, B)

            return var*tomato

        self.container.singleton(A)
        self.container.factory(B)

        assert self.container.bind(test)('x', tomato=5) == "xxxxx"

    def test_it_should_treat_attribute_access_as_get(self):
        class A:
            pass

        self.container.factory(A, 'ay')
        assert isinstance(self.container.ay, A)

    def test_it_should_treat_call_as_get(self):
        class A:
            pass

        self.container.factory(A, 'ay')
        assert isinstance(self.container('ay'), A)

    def test_it_should_correctly_give_existence_checks(self):
        class A:
            pass

        class B:
            pass

        class C(B):
            pass

        class D:
            pass

        self.container.singleton(A)
        self.container.factory(C)

        assert A in self.container
        assert D not in self.container


