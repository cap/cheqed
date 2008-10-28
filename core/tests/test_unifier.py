from nose.tools import assert_equal, assert_raises

from cheqed.core.unification import Unifier, UnificationError

def is_variable(x):
    return isinstance(x, str)

def occurs_in(x, y):
    return x in str(y)

def unify(subs):
    unifier = Unifier(is_variable, occurs_in)
    for a, b in subs:
        unifier.unify(a, b)
    return unifier.get_substitutions()

def test_unify():
    assert_equal(unify([]), {})
    assert_equal(unify([(0, 0)]), {})
    assert_equal(unify([('x', 'x')]), {})
    assert_equal(unify([('x', 0)]), {'x': 0})
    assert_equal(unify([(0, 'x')]), {'x': 0})
    assert_equal(unify([('x', 'y')]), {'x': 'y'})
    assert_equal(unify([('x', 'y'), ('x', 0)]), {'x': 0, 'y': 0})
    assert_equal(unify([('x', 'y'), ('y', 0)]), {'x': 0, 'y': 0})
    assert_equal(unify([('x', 'y'), ('y', 'z'), ('z', 0)]),
                 {'x': 0, 'y': 0, 'z': 0})
    assert_equal(unify([('x', 'y'), ('y', 'x')]), {'x': 'y'})
    assert_equal(unify([('x', 'y'), ('y', 'x')]), {'x': 'y'})

    assert_raises(UnificationError, unify, [(0, 1)])
    assert_raises(UnificationError, unify, [('x', 0), ('x', 1)])
    assert_raises(UnificationError, unify, [('x', 'y'), ('x', 0), ('y', 1)])
    assert_raises(UnificationError, unify, [('x', 'xy')])
