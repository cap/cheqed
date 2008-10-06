from py.test import raises

from cheqed.core.sequent import Sequent
from cheqed.core import unification, environment
from cheqed.core.rules import primitive

def setup_module(module):
    module.env = environment.load_modules('logic', 'set')
    module.pt = env.parser.parse

def test_negation():
    assert (primitive.right_negation(Sequent([], [pt('not x')]))
            == [Sequent([pt('x:bool')], [])])

def test_disjunction():
    assert (primitive.left_disjunction(Sequent([pt('a or b')], []))
            == [Sequent([pt('a:bool')], []),
                Sequent([pt('b:bool')], [])])

    raises(unification.UnificationError,
           primitive.left_disjunction,
           Sequent([pt('a and b')], []))

    assert (primitive.right_disjunction(Sequent([], [pt('a or b')]))
            == [Sequent([], [pt('a:bool'), pt('b:bool')])])

    raises(unification.UnificationError,
           primitive.right_disjunction,
           Sequent([], [pt('a and b')]))

def test_universal():
    uni = pt('for_all x . phi(x)')
    wit = pt('f:obj->obj(y)')
    res = pt('phi:obj->bool(f:obj->obj(y:obj))')
    
    assert (primitive.left_universal(Sequent([uni], []), wit)
            == [Sequent([res, uni], [])])

    raises(unification.UnificationError,
           primitive.right_universal, Sequent([], [uni]), wit)

    wit = pt('a:obj')
    res = pt('phi:obj->bool(a)')
    assert (primitive.right_universal(Sequent([], [uni]), wit)
            == [Sequent([], [res])])

def test_substitution():
    exists_def = pt(r'(exists) = (\x . not (for_all y . not x(y)))')
    term = pt(r'exists x . (for_all y . not (y in x))')

    primitive.right_substitution(Sequent([exists_def], [term]))
    
