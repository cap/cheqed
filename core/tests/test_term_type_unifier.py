from nose.tools import assert_true, assert_equal, assert_not_equal, assert_raises
from py.test import raises

from cheqed.core import environment, qterm, term_builder, qtype, unification
from cheqed.core.qtype import qbool, qobj, qfun, qvar
from cheqed.core.qterm import Atom, Variable, Constant, Abstraction, Combination
from cheqed.core.unification import UnificationError
from cheqed.core.term_type_unifier import unify_types

        
def setup_module(module):
    env = environment.load_modules('logic', 'set')
    module.pt = env.parser.parse
    module.pq = env.parser.parse_type
    
class TestVariable:
    def setup(self):
        self.cls = qterm.Variable

        self.x_obj = self.cls('x', pq('obj'))
        self.x_bool = self.cls('x', pq('bool'))
        self.x_bool_obj = self.cls('x', pq('bool->obj'))
        self.x_var = self.cls('x', pq('?a'))
        self.y_obj = self.cls('y', pq('obj'))
        self.y_var = self.cls('y', pq('?a'))
    
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
        
