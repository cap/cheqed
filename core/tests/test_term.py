from py.test import raises

from cheqed.core import environment, qterm, qtype, unification
from cheqed.core.qtype import qbool, qobj, qfun, qvar
from cheqed.core.qterm import Variable, Constant, Abstraction, Combination, free_variables

def setup_module(module):
    env = environment.load_modules('logic', 'set')
    module.pt = env.parser.parse
    module.pq = env.parser.parse_type

def test_match1():
    x_const = qterm.Constant('x', pq('obj'))
    x_var = qterm.Variable('x', pq('obj'))

    assert qterm.match(x_var, x_const) == {'x':x_const}
    raises(unification.UnificationError,
           qterm.match, x_const, x_var)
    
    f = qterm.Constant('f', pq('obj->obj'))
    y = qterm.Variable('y', pq('obj'))
    f_x = qterm.Combination(f, x_var)
    f_y = qterm.Combination(f, y)
    assert qterm.match(f_x, f_y) == {'x':y}
    raises(unification.UnificationError,
           qterm.match, f_x, y)

def test_match():
    a = pt(r'a:bool')
    not_a = pt(r'not a')

    raises(unification.UnificationError, qterm.match, not_a, a)

def test_equality_match():
    pattern = pt(r'a = b')

    term = pt(r'c = d')
    match = qterm.match(pattern, term)
    assert match['a'].name == 'c'
    assert match['b'].name == 'd'

    term = pt(r'c = c')
    match = qterm.match(pattern, term)
    assert match['a'].name == 'c'
    assert match['b'].name == 'c'

    term = pt(r'c = (\x.phi)')
    match = qterm.match(pattern, term)
    assert match['a'].name == 'c'
    assert qterm.is_abstraction(match['b'])
    
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
    
    def test_unify(self):
        x_obj = self.cls('x', pq('obj'))
        x_bool = self.cls('x', pq('bool'))
        x_var = self.cls('x', pq('?a'))
        y_var = self.cls('y', pq('?a'))

        assert qterm.unify(x_obj, x_obj) == x_obj
        raises(qtype.UnificationError, qterm.unify, x_obj, x_bool)
        raises(qtype.UnificationError, qterm.unify, y_var, x_bool)
        raises(qtype.UnificationError, qterm.unify, x_var, x_bool)

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
    
    def test_unify(self):
        assert qterm.unify(self.x_obj, self.x_obj) == self.x_obj
        assert qterm.unify(self.x_var, self.x_bool) == self.x_bool
        assert qterm.unify(self.y_var, self.x_obj) == self.x_obj

        raises(qtype.UnificationError, qterm.unify, self.x_obj, self.x_bool)
        raises(qtype.UnificationError, qterm.unify, self.y_obj, self.x_bool)

    def test_unify_types(self):
        f1 = qterm.Variable('f', qfun(qvar(), qvar()))
        f2 = qterm.Variable('f', qfun(qvar(), qvar()))
        assert f1 != f2

        f1u, f2u = qterm.unify_types([f1, f2])
        assert f1u == f2u

        # this is a particularly tricky situation
        v1 = qvar()
        v2 = qvar()
        g1 = qterm.Variable('g', qfun(v1, v2))
        g2 = qterm.Variable('g', qfun(v2, qobj()))
        assert g1 != g2

        g1u, g2u = qterm.unify_types([g1, g2])
        assert g1u == g2u

    def test_unify_types2(self):
        x1 = qterm.Variable('x', qvar())
        x2 = qterm.Variable('x', qvar())
        assert x1 != x2

        x1u, x2u = qterm.unify_types([x1, x2])
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
    
    def test_unify(self):
        f = qterm.Constant('f', pq('obj->bool'))
        x = qterm.Variable('x', pq('obj'))
        f_x = qterm.Combination(f, x)

        assert qterm.unify(f_x, f_x) == f_x
        
        g = qterm.Constant('g', pq('obj->obj'))
        g_x = qterm.Combination(g, x)

        raises(qtype.UnificationError, qterm.unify, f, g)

        y = qterm.Variable('y', pq('obj'))
        g_y = qterm.Combination(g, y)

        assert qterm.unify(g_x, g_y) == g_y

        f_g_y = qterm.Combination(f, g_y)

        assert qterm.unify(f_x, f_g_y) == f_g_y

        h = qterm.Variable('h', pq('?a'))
        h_x = qterm.Combination(h, x)

        assert qterm.unify(h_x, g_x) == g_x

    def test_unify2(self):
        f1 = qterm.Variable('f', qtype.qvar())
        f2 = qterm.Variable('f', qtype.qvar())
        x = qterm.Variable('x', qtype.qobj())
        f2_x = qterm.Combination(f2, x)
        assert f2_x.qtype.is_variable
        f1_f2_x = qterm.Combination(f1, f2_x)
        assert f1_f2_x.qtype == qtype.qobj()
        assert f1_f2_x.operator.qtype == f1_f2_x.operand.operator.qtype

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
        b = a.substitute(x, y)
        assert b.bound != x

    def test_equality(self):
        pass
    
    def test_unify(self):
        x = qterm.Variable('x', pq('obj'))
        phi = qterm.Variable('phi', pq('bool'))
        b_x_phi = qterm.Abstraction(x, phi)

        assert qterm.unify(b_x_phi, b_x_phi) == b_x_phi

        psi = qterm.Variable('psi', pq('bool'))
        b_x_psi = qterm.Abstraction(x, psi)
        
        assert qterm.unify(b_x_phi, b_x_psi) == b_x_psi

        y = qterm.Variable('y', pq('obj'))
        b_y_phi = qterm.Abstraction(y, phi)

        assert qterm.unify(b_y_phi, b_x_phi) == b_x_phi

def test_fancy_unification():
    x = qterm.Variable('x', pq('obj'))

    assert qterm.unify(x, x) == x

    y = qterm.Variable('y', pq('obj'))

    assert qterm.unify(x, y) == y

    z = qterm.Variable('z', pq('bool'))

    raises(unification.UnificationError, qterm.unify, x, z)

    f = qterm.Constant('f', pq('obj->obj'))
    f_y = qterm.Combination(f, y)

    assert qterm.unify(x, f_y) == f_y
    raises(unification.UnificationError, qterm.unify, z, f_y)

    b_x_z = qterm.Abstraction(x, z)
    b_y_z = qterm.Abstraction(y, z)
    assert qterm.unify(b_x_z, b_y_z) == b_y_z

    a = pt('f:obj->obj->obj(x, g(y:bool))')
    b = pt('f:obj->obj->obj(h(w:bool), z)')
    c = pt('f:obj->obj->obj(h(w:bool), g(y:bool))')
    assert qterm.unify(a, b) == c

    d = pt('f(h(w:bool), g(y:bool))')
    assert qterm.unify(c, d) == c

def test_match():
    a = pt('f:obj->obj->obj(x, g(y))')
    b = pt('f(x, x)')
    raises(unification.UnificationError, qterm.match, b, a)
    c = pt('f(x, y)')
    
class TestUnification:
    def test_atom(self):
        x_obj = qterm.Constant('x', pq('obj'))
        x_bool = qterm.Constant('x', pq('bool'))
        x_var = qterm.Constant('x', pq('?a'))
        x_var2 = qterm.Constant('x', pq('?a'))
        y_bool = qterm.Constant('y', pq('bool'))

        x, y = qterm.unify_types([x_obj, y_bool])
        assert x == x_obj
        assert y == y_bool
        
#        raises(qtype.UnificationError, qterm.unify_types, [x_obj, x_bool])
        xa, xb = qterm.unify_types([x_obj, x_var])
        assert xa == x_obj
        assert xb == x_var

        assert x_var != x_var2
        xa, xb = qterm.unify_types([x_var, x_var2])
        assert xa == x_var

    def test_combo(self):
        x_obj = qterm.Variable('x', pq('obj'))
        x_var = qterm.Variable('x', pq('?a'))
        phi_var = qterm.Constant('phi', pq('?b->bool'))
        phi_obj = qterm.Constant('phi', pq('obj->bool'))
        combo_var = qterm.Combination(phi_var, x_var)
        combo_obj = qterm.Combination(phi_obj, x_obj)
        combo_var2 = qterm.Combination(phi_var, x_obj)

        x, combo = qterm.unify_types([x_obj, combo_var])
        assert x == x_obj
        assert combo == combo_obj

        phi_a, phi_b = qterm.unify_types([phi_var, phi_obj])
        assert phi_a == phi_var
        assert phi_b == phi_obj

        combo_a, combo_b = qterm.unify_types([combo_var, combo_obj])
        assert combo_a == combo_obj
        assert combo_b == combo_obj

        combo_a, combo_b = qterm.unify_types([combo_var2, combo_obj])
        assert combo_a == combo_obj
        assert combo_b == combo_obj

        f = qterm.Variable('f', pq('?x->?y'))
        raises(qtype.UnificationError, qterm.Combination, f, f)
        raises(qtype.UnificationError, qterm.Combination, x_var, x_var)
        
        
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
    
    raises(qtype.UnificationError, qterm.Combination, x_obj, x_obj)
    raises(qtype.UnificationError, qterm.Combination, f_bool_bool, x_obj)

    assert qterm.Combination(f_bool_bool, x_bool).qtype == qbool

def test_abstraction_qtype():
    qobj = qtype.qobj()
    qbool = qtype.qbool()

    x_const_obj = qterm.Constant('x', qobj)
    x_var_bool = qterm.Variable('x', qbool)
    f_var_bool_bool = qterm.Variable('f', qtype.qfun(qbool, qbool))
    x_var_obj = qterm.Variable('x', qobj)

    y_const_bool = qterm.Constant('y', qbool)
    
    raises(qtype.UnificationError, qterm.Abstraction, x_const_obj, y_const_bool)
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

    rx = qterm.Combination(qrel, qx)

    assert free_variables(rx) == set([qx])

from cheqed.core.qterm import Constant, Variable, Combination, Abstraction

def test_substitute():
    term = pt(r'for_all x . (x in a)')
    x = pt(r'x:obj')
    b = pt(r'b:obj')

    result = term.substitute(b, x)

    assert result == term

def test_variable_set():
    xa = Variable('x', qtype.qobj())
    xb = Variable('x', qtype.qobj())

    assert hash(xa) == hash(xb)
    assert xa in set([xb])
