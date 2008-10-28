from nose.tools import assert_true, assert_equal, assert_not_equal, assert_raises
from py.test import raises

from cheqed.core import environment, qterm, term_builder, qtype, unification
from cheqed.core.qtype import qbool, qobj, qfun, qvar
from cheqed.core.qterm import Variable, Constant, Abstraction, Combination, free_variables
from cheqed.core.unification import UnificationError
from cheqed.core.term_type_unifier import unify_types

class TestConstant_:
    def test_immutable(self):
        const = Constant('a', 'obj')
        assert_raises(AttributeError, setattr, const, 'name', None)
        assert_raises(AttributeError, setattr, const, 'qtype', None)

    def test_equality(self):
        assert_equal(Constant('a', 'obj'),
                     Constant('a', 'obj'))

        assert_not_equal(Constant('a', 'obj'),
                         Constant('b', 'obj'))

        assert_not_equal(Constant('a', 'obj'),
                         Constant('a', 'bool'))

        assert_not_equal(Constant('a', 'obj'),
                         Variable('a', 'obj'))

    def test_set_membership(self):
        assert_true(Constant('a', 'obj') in set([Constant('a', 'obj')]))


class TestVariable_:
    def test_immutable(self):
        var = Variable('a', 'obj')
        assert_raises(AttributeError, setattr, var, 'name', None)
        assert_raises(AttributeError, setattr, var, 'qtype', None)

    def test_equality(self):
        assert_equal(Variable('a', 'obj'),
                     Variable('a', 'obj'))

        assert_not_equal(Variable('a', 'obj'),
                         Variable('b', 'obj'))

        assert_not_equal(Variable('a', 'obj'),
                         Variable('a', 'bool'))

        assert_not_equal(Variable('a', 'obj'),
                         Constant('a', 'obj'))

    def test_set_membership(self):
        assert_true(Variable('a', 'obj') in set([Variable('a', 'obj')]))


class TestCombination_:
    def test_immutable(self):
        comb = Combination('a', 'b')
        assert_raises(AttributeError, setattr, comb, 'operator', None)
        assert_raises(AttributeError, setattr, comb, 'operand', None)
    
    def test_equality(self):
        assert_equal(Combination('a', 'b'),
                     Combination('a', 'b'))

        assert_not_equal(Combination('a', 'b'),
                         Combination('c', 'b'))

        assert_not_equal(Combination('a', 'b'),
                         Combination('a', 'c'))

    def test_set_membership(self):
        assert_true(Combination('a', 'b') in set([Combination('a', 'b')]))

        
class TestAbstraction_:
    def test_immutable(self):
        abs = Abstraction(Variable('a', 'obj'), 'b')
        assert_raises(AttributeError, setattr, abs, 'body', None)
        assert_raises(AttributeError, setattr, abs, 'bound', None)
    
    def test_equality(self):
        assert_equal(Abstraction(Variable('a', 'obj'), 'b'),
                     Abstraction(Variable('a', 'obj'), 'b'))

        assert_not_equal(Abstraction(Variable('a', 'obj'), 'b'),
                         Abstraction(Variable('c', 'obj'), 'b'))

        assert_not_equal(Abstraction(Variable('a', 'obj'), 'b'),
                         Abstraction(Variable('a', 'obj'), 'c'))

    def test_set_membership(self):
        assert_true(Abstraction(Variable('a', 'obj'), 'b')
                    in set([Abstraction(Variable('a', 'obj'), 'b')]))


def setup_module(module):
    env = environment.load_modules('logic', 'set')
    module.pt = env.parser.parse
    module.pq = env.parser.parse_type
    
class TestConstant:
    def setup(self):
        self.cls = qterm.Constant

    def test_free_variables(self):
        assert free_variables(self.cls('x', pq('obj'))) == set()
        assert free_variables(self.cls('x', pq('bool'))) == set()

    def test_substitute(self):
        pass

    def test_equality(self):
        x_obj = self.cls('x', pq('obj'))
        x_bool = self.cls('x', pq('bool'))

        assert x_obj == x_obj
        assert x_bool == x_bool
        assert x_obj != x_bool
    
class TestVariable:
    def setup(self):
        self.cls = qterm.Variable

        self.x_obj = self.cls('x', pq('obj'))
        self.x_bool = self.cls('x', pq('bool'))
        self.x_bool_obj = self.cls('x', pq('bool->obj'))
        self.x_var = self.cls('x', pq('?a'))
        self.y_obj = self.cls('y', pq('obj'))
        self.y_var = self.cls('y', pq('?a'))
        
    def test_qtype(self):
        assert self.x_obj.qtype == pq('obj')
        assert self.x_bool.qtype == pq('bool')
        assert self.x_bool_obj.qtype == pq('bool->obj')
        
    def test_free_variables(self):
        assert free_variables(self.x_obj) == set([self.x_obj])

    def test_substitute(self):
        pass

    def test_equality(self):
        assert self.x_obj == self.x_obj
        assert self.x_bool == self.x_bool
        assert self.x_obj != self.x_bool
    
    def test_unify_types(self):
        f1 = qterm.Variable('f', qfun(qvar(), qvar()))
        f2 = qterm.Variable('f', qfun(qvar(), qvar()))
        assert f1 != f2

        f1u, f2u = unify_types([f1, f2])
        assert f1u == f2u

        # this is a particularly tricky situation
        v1 = qvar()
        v2 = qvar()
        g1 = qterm.Variable('g', qfun(v1, v2))
        g2 = qterm.Variable('g', qfun(v2, qobj()))
        assert g1 != g2

        g1u, g2u = unify_types([g1, g2])
        assert g1u == g2u

    def test_unify_types2(self):
        x1 = qterm.Variable('x', qvar())
        x2 = qterm.Variable('x', qvar())
        assert x1 != x2

        x1u, x2u = unify_types([x1, x2])
        assert x1u == x2u

class TestCombination:
    def setup_method(self, method):
        self.cls = qterm.Variable

        self.x_obj = self.cls('x', pq('obj'))
        self.x_bool = self.cls('x', pq('bool'))
        self.x_bool_obj = self.cls('x', pq('bool->obj'))
        self.x_var = self.cls('x', pq('?a'))
        self.y_obj = self.cls('y', pq('obj'))
        self.y_var = self.cls('y', pq('?a'))
        
    def test_qtype(self):
        assert pt('f:obj->bool(x)').qtype == pq('bool')
        
    def test_free_variables(self):
        f = qterm.Constant('f', pq('obj->bool'))
        g = qterm.Constant('g', pq('obj->obj'))
        x = qterm.Variable('x', pq('obj'))

        assert free_variables(qterm.Combination(f, x)) == set([x])
        assert free_variables(qterm.Combination(f, qterm.Combination(g, x))) \
            == set([x])

    def test_substitute(self):
        pass

    def test_equality(self):
        f = qterm.Constant('f', pq('obj->bool'))
        g = qterm.Constant('g', pq('obj->obj'))
        x = qterm.Variable('x', pq('obj'))

        f_x = qterm.Combination(f, x)
        f_x2 = qterm.Combination(f, x)
        g_x = qterm.Combination(g, x)
        f_g_x = qterm.Combination(f, qterm.Combination(g, x))

        assert f_x == f_x
        assert not f_x != f_x
        assert f_x == f_x2
        assert not f_x != f_x2
        assert f_x != g_x

class TestAbstraction:
    def setup_method(self, method):
        pass
    
    def test_qtype(self):
        pass
        
    def test_free_variables(self):
        pass
    
    def test_substitute(self):
        x = Variable('x', qobj())
        y = Variable('y', qobj())
        phi = Variable('phi', qfun(qobj(), qbool()))
        phi_y = Combination(phi, y)
        a = Abstraction(x, phi_y)
        b = qterm.substitute(a, x, y)
        assert b.bound != x

    def test_equality(self):
        pass
    
class TestUnification:
    def test_atom(self):
        x_obj = qterm.Constant('x', pq('obj'))
        x_bool = qterm.Constant('x', pq('bool'))
        x_var = qterm.Constant('x', pq('?a'))
        x_var2 = qterm.Constant('x', pq('?a'))
        y_bool = qterm.Constant('y', pq('bool'))

        x, y = unify_types([x_obj, y_bool])
        assert x == x_obj
        assert y == y_bool
        
#        raises(qtype.UnificationError, unify_types, [x_obj, x_bool])
        xa, xb = unify_types([x_obj, x_var])
        assert xa == x_obj
        assert xb == x_var

        assert x_var != x_var2
        xa, xb = unify_types([x_var, x_var2])
        assert xa == x_var

    def test_combo(self):
        x_obj = qterm.Variable('x', pq('obj'))
        x_var = qterm.Variable('x', pq('?a'))
        phi_var = qterm.Constant('phi', pq('?b->bool'))
        phi_obj = qterm.Constant('phi', pq('obj->bool'))
        combo_var = term_builder.build_combination(phi_var, x_var)
        combo_obj = term_builder.build_combination(phi_obj, x_obj)
        combo_var2 = term_builder.build_combination(phi_var, x_obj)

        x, combo = unify_types([x_obj, combo_var])
        assert x == x_obj
        assert combo == combo_obj

        phi_a, phi_b = unify_types([phi_var, phi_obj])
        assert phi_a == phi_var
        assert phi_b == phi_obj

        combo_a, combo_b = unify_types([combo_var, combo_obj])
        assert combo_a == combo_obj
        assert combo_b == combo_obj

        combo_a, combo_b = unify_types([combo_var2, combo_obj])
        assert combo_a == combo_obj
        assert combo_b == combo_obj

        f = qterm.Variable('f', pq('?x->?y'))
        raises(UnificationError, term_builder.build_combination, f, f)
        raises(UnificationError, term_builder.build_combination, x_var, x_var)
        
        
    def test_abstraction(self):
        x_obj = qterm.Variable('x', pq('obj'))
        x_var = qterm.Variable('x', pq('?a'))
        phi_bool = qterm.Constant('phi', pq('bool'))
        phi_var = qterm.Constant('phi', pq('?b'))
        abstraction_var = qterm.Abstraction(x_var, phi_var)
        abstraction_obj_bool = qterm.Abstraction(x_obj, phi_bool)
        

        
def test_simple_qtypes():
    qobj = qtype.qobj()
    qbool = qtype.qbool()

    def check(cls, qtype_):
        assert cls('x', qtype_).qtype == qtype_
    
    for cls in [qterm.Variable, qterm.Constant]:
        for qtype_ in [qobj, qbool, qtype.qfun(qobj, qbool)]:
            yield check, cls, qtype_

def test_combination_qtype():
    qobj = qtype.qobj()
    qbool = qtype.qbool()

    x_obj = qterm.Constant('x', qobj)
    x_bool = qterm.Constant('x', qbool)
    f_bool_bool = qterm.Constant('f', qtype.qfun(qbool, qbool))
    
    raises(TypeError, term_builder.build_combination, x_obj, x_obj)
    raises(unification.UnificationError, term_builder.build_combination, f_bool_bool, x_obj)

    assert term_builder.build_combination(f_bool_bool, x_bool).qtype == qbool

def test_abstraction_qtype():
    qobj = qtype.qobj()
    qbool = qtype.qbool()

    x_const_obj = qterm.Constant('x', qobj)
    x_var_bool = qterm.Variable('x', qbool)
    f_var_bool_bool = qterm.Variable('f', qtype.qfun(qbool, qbool))
    x_var_obj = qterm.Variable('x', qobj)

    y_const_bool = qterm.Constant('y', qbool)
    
    raises(TypeError, qterm.Abstraction, x_const_obj, y_const_bool)
    assert (qterm.Abstraction(x_var_obj, y_const_bool).qtype
            == qtype.qfun(qobj, qbool))

def test_ops():
    qbool = qtype.qbool()
    qobj = qtype.qobj()

    unop = qtype.qfun(qbool, qbool)
    binop = qtype.qfun(qbool, unop)

    unrel = qtype.qfun(qobj, qbool)
    binrel = qtype.qfun(qobj, unrel)

    qrel = qterm.Constant('phi', unrel)
    qor = qterm.Constant('or', binop)
    qx = qterm.Variable('x', qobj)

    rx = term_builder.build_combination(qrel, qx)

    assert free_variables(rx) == set([qx])

from cheqed.core.qterm import Constant, Variable, Combination, Abstraction

def test_substitute():
    term = pt(r'for_all x . (x in a)')
    x = pt(r'x:obj')
    b = pt(r'b:obj')

    result = qterm.substitute(term, b, x)

    assert result == term

