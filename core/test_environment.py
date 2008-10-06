from cheqed.core import qterm, qtype
from cheqed.core.environment import _load, _load_single

test_module = r'''
constant('=:?a->?a->bool')
operator('=', 2, 'left', 200)

constant('foo:bool->bool')
operator('foo', 1, 'right', 100)
definition(r'(foo) = (\x bar(x))')
axiom('foo_property', r'foo x = x')
'''

def check_configuration_lens(configuration):
    assert len(configuration.constants) == 2
    assert len(configuration.definitions) == 1
    assert len(configuration.operators) == 2

def test__load_single():
    # Load and verify two configurations in a row to make sure loads
    # are independent.
    for i in range(2):
        check_configuration_lens(_load_single(test_module))

def test__load():
    # Load and verify two configurations in a row to make sure loads
    # are independent.
    for i in range(2):
        check_configuration_lens(_load([test_module]))
        
def test_load():
    environment = _load([test_module]).make_environment()

    foo = qterm.Constant('foo', qtype.qfun(qtype.qbool(), qtype.qbool()))
    bar = qterm.Variable('bar', qtype.qfun(qtype.qbool(), qtype.qbool()))
    x = qterm.Variable('x', qtype.qbool())
    definition = qterm.binary_op(environment.constants['='],
                                 foo,
                                 qterm.Abstraction(x, qterm.unary_op(bar, x)))
    
    assert environment.constants['foo'] == foo
    assert environment.definitions['foo'] == definition
