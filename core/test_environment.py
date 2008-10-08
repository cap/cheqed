from nose.tools import assert_true, assert_equal

from cheqed.core import qterm, qtype
from cheqed.core.environment import _load, _load_single, Environment

test_module = r'''
constant('=:?a->?a->bool')
operator('=', 2, 'left', 200)

constant('foo:bool->bool')
operator('foo', 1, 'right', 100)
definition(r'(foo) = (\x bar(x))')
axiom('foo_property', r'foo x = x')
'''

        
def test_load():
    environment = _load([test_module])

    foo = qterm.Constant('foo', qtype.qfun(qtype.qbool(), qtype.qbool()))
    bar = qterm.Variable('bar', qtype.qfun(qtype.qbool(), qtype.qbool()))
    x = qterm.Variable('x', qtype.qbool())
    definition = qterm.binary_op(environment.constants['='],
                                 foo,
                                 qterm.Abstraction(x, qterm.unary_op(bar, x)))
    
    assert environment.constants['foo'] == foo
    assert environment.definitions['foo'] == definition


def test_load_rules():
    rules = '''
@primitive
def prim(goal):
    pass
'''
    env = Environment()
    env.load_rules(rules)
    prim = env.rules['prim']
    assert_true(prim.is_primitive)
