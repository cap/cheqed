from py.test import raises

from cheqed.core import unification

def is_variable(x):
    return isinstance(x, str)

def unify(subs):
    return unification.unify(subs, is_variable, lambda a, b: a in str(b))

def test_unify():
    expected = [
        ([], {}),
        ([(0, 0)], {}),
        ([('x', 'x')], {}),
        ([('x', 0)], {'x': 0}),
        ([(0, 'x')], {'x': 0}),
        ([('x', 'y')], {'x': 'y'}),
        ([('x', 'y'), ('x', 0)], {'x': 0, 'y': 0}),
        ([('x', 'y'), ('y', 0)], {'x': 0, 'y': 0}),
        ([('x', 'y'), ('y', 'z'), ('z', 0)], {'x': 0, 'y': 0, 'z': 0}),
        ([('x', 'y'), ('y', 'x')], {'x': 'y'}),
        ]

    for subs, result in expected:
        assert unify(subs) == result

    errors = [
        [(0, 1)],
        [('x', 0), ('x', 1)],
        [('x', 'y'), ('x', 0), ('y', 1)],
        [('x', 'xy')],
        ]

    for subs in errors:
        raises(unification.UnificationError, unify, subs)
