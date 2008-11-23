from nose.tools import assert_true, assert_equal, assert_not_equal, \
    assert_raises

from cheqed.core import qtype
from cheqed.core.qtype import qbool, qobj, qfun, qvar
from cheqed.core.qterm import Atom, Variable, Constant, Abstraction, Combination

def type_a():
    return qtype.Constant('a')

def type_b():
    return qtype.Constant('b')

class TestAtom:
    def test_immutability(self):
        atom = Atom('a', type_a())
        assert_raises(AttributeError, setattr, atom, 'name', None)
        assert_raises(AttributeError, setattr, atom, 'qtype', None)

    def test_equality(self):
        assert_equal(Atom('a', type_a()),
                     Atom('a', type_a()))

        assert_not_equal(Atom('a', type_a()),
                         Atom('b', type_a()))

        assert_not_equal(Atom('a', type_a()),
                         Atom('a', type_b()))

        assert_not_equal(Constant('a', type_a()),
                         Variable('a', type_a()))

    def test_set_membership(self):
        assert_true(Atom('a', type_a()) in set([Atom('a', type_a())]))

    def test_atoms(self):
        assert_equal(Atom('a', type_a()).atoms(),
                     set([Atom('a', type_a())]))
        

class TestConstant:
    def test_free_variables(self):
        assert_equal(Constant('a', type_a()).free_variables(), set())

        
class TestVariable:
    def test_free_variables(self):
        assert_equal(Variable('a', type_a()).free_variables(),
                     set([Variable('a', type_a())]))


class TestCombination:
    def make_fun(self, name, arg_type, result_type):
        return Constant(name, qfun(arg_type, result_type))

    def make_call(self, func_name, arg_name,
                  arg_type=type_a(), result_type=type_a()):
        return Combination(self.make_fun(func_name, arg_type, result_type),
                           Constant(arg_name, arg_type))

    def test_constructor(self):
        # operator is not a function
        assert_raises(TypeError, Combination,
                      Constant('a', type_a()),
                      Constant('b', type_b()))

        # operand is wrong type
        assert_raises(TypeError, Combination,
                      Constant('a', qfun(type_a(), type_b())),
                      Constant('d', type_b()))

    def test_immutable(self):
        comb = self.make_call('a', 'b')
        assert_raises(AttributeError, setattr, comb, 'operator', None)
        assert_raises(AttributeError, setattr, comb, 'operand', None)
        assert_raises(AttributeError, setattr, comb, 'qtype', None)
    
    def test_equality(self):
        assert_equal(self.make_call('a', 'b'),
                     self.make_call('a', 'b'))

        assert_not_equal(self.make_call('a', 'b'),
                         self.make_call('c', 'b'))

        assert_not_equal(self.make_call('a', 'b'),
                         self.make_call('a', 'c'))

    def test_set_membership(self):
        assert_true(self.make_call('a', 'b')
                    in set([self.make_call('a', 'b')]))

    def test_free_variables(self):
        assert_equal(Combination(Variable('a', qfun(type_a(), type_a())),
                                 Constant('b', type_a())).free_variables(),
                     set([Variable('a', qfun(type_a(), type_a()))]))        

        assert_equal(Combination(Constant('a', qfun(type_a(), type_a())),
                                 Variable('b', type_a())).free_variables(),
                     set([Variable('b', type_a())]))

        assert_equal(Combination(Variable('a', qfun(type_a(), type_a())),
                                 Variable('b', type_a())).free_variables(),
                     set([Variable('a', qfun(type_a(), type_a())),
                          Variable('b', type_a())]))


class TestAbstraction:
    def make_abstraction(self, bound_name, body_name,
                         bound_type=type_a(), body_type=type_a()):
        return Abstraction(Variable(bound_name, bound_type),
                           Constant(body_name, body_type))

    def test_constructor(self):
        assert_raises(TypeError, Abstraction,
                      Constant('a', type_a()),
                      Constant('b', type_a()))
    
    def test_immutable(self):
        abs = self.make_abstraction('a', 'b')
        assert_raises(AttributeError, setattr, abs, 'body', None)
        assert_raises(AttributeError, setattr, abs, 'bound', None)
        assert_raises(AttributeError, setattr, abs, 'qtype', None)

    def test_equality(self):
        assert_equal(self.make_abstraction('a', 'b'),
                     self.make_abstraction('a', 'b'))

        assert_not_equal(self.make_abstraction('a', 'b'),
                         self.make_abstraction('c', 'b'))

        assert_not_equal(self.make_abstraction('a', 'b'),
                         self.make_abstraction('a', 'c'))

    def test_set_membership(self):
        assert_true(self.make_abstraction('a', 'b')
                    in set([self.make_abstraction('a', 'b')]))

    def test_free_variables(self):
        assert_equal(Abstraction(Variable('a', type_a()),
                                 Variable('a', type_a())).free_variables(),
                     set())

        assert_equal(Abstraction(Variable('a', type_a()),
                                 Variable('b', type_a())).free_variables(),
                     set([Variable('b', type_a())]))

        # same name, different type means what?
        # isn't this an invalid term?
        assert_equal(Abstraction(Variable('a', type_a()),
                                 Variable('a', type_b())).free_variables(),
                     set([Variable('a', type_b())]))
