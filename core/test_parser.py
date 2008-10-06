from cheqed.core import parser, qtype, qterm

from cheqed.core.qterm import Constant
from cheqed.core.qtype import qbool, qobj, qfun, qvar
from cheqed.core.syntax import Syntax, Binder, Operator, Type

class TestParse:
    @classmethod
    def setup_class(cls):
        cls.for_all = Constant('for_all', qfun(qfun(qobj(), qbool()), qbool()))
        cls.exists = Constant('exists',  qfun(qfun(qobj(), qbool()), qbool()))
        cls.not_ = Constant('not', qfun(qbool(), qbool()))
        eqvar = qvar()
        cls.equals = Constant('=', qfun(eqvar, qfun(eqvar, qbool())))
        
        extensions = [
            Type(qbool, 'bool'),
            Type(qobj, 'obj'),
            Binder(cls.for_all),
            Binder(cls.exists),
            Operator(cls.not_, 1, 'right', 100),
            Operator(cls.equals, 2, 'left', 200),
            ]
            
        cls.parser = parser.Parser(Syntax(extensions))

    def test_parse_constant_type(self):
        matches = [
            ('bool', qbool()),
            ('(bool)', qbool()),
            ('obj', qobj()),
            ('obj->obj', qfun(qobj(), qobj())),
            ('obj->obj->obj', qfun(qobj(), qfun(qobj(), qobj()))),
            ('(obj->obj)->obj', qfun(qfun(qobj(), qobj()), qobj())),        
            ('obj->bool', qfun(qobj(), qbool())),
            ]

        for string, obj in matches:
            assert self.parser.parse_type(string) == obj

    def test_parse_variable_type(self):
        assert isinstance(self.parser.parse_type('?a'), qtype.QTypeVariable)

        fun = self.parser.parse_type('?a->?a')
        assert fun.args[0] == fun.args[1]

        fun = self.parser.parse_type('?a->?b')
        assert fun.args[0] != fun.args[1]

        fun2 = self.parser.parse_type('?a->?b')
        assert fun.args[0] != fun2.args[0]
        assert fun.args[1] != fun2.args[1]

    def test_parse_untyped_variable(self):
        var = self.parser.parse('var')
        assert var.name == 'var'
        assert var.qtype.is_variable

    def test_parse_typed_variable(self):
        var = self.parser.parse('var:bool')
        assert var.name == 'var'
        assert var.qtype == qbool()

        var = self.parser.parse('var:bool->obj')
        assert var.name == 'var'
        assert var.qtype == qfun(qbool(), qobj())

    def test_parse_operator(self):
        assert (self.parser.parse('not a')
                == qterm.unary_op(self.not_,
                                   qterm.Variable('a', qbool())))
        
        assert (self.parser.parse('a:obj = b:obj')
                == qterm.binary_op(self.equals,
                                   qterm.Variable('a', qobj()),
                                   qterm.Variable('b', qobj())))

    def test_parse_binder(self):
        assert (self.parser.parse('for_all x phi')
                == qterm.binder(self.for_all,
                                qterm.Variable('x', qobj()),
                                qterm.Variable('phi', qbool())))

    def test_parse_function(self):
        t = qfun(qobj(), qobj())
        f = qterm.Variable('f', t)
        g = qterm.Variable('g', t)
        h = qterm.Variable('h', qfun(qobj(), t))
        x = qterm.Variable('x', qobj())
        y = qterm.Variable('y', qobj())

        assert (self.parser.parse('f:obj->obj(x)')
                == qterm.unary_op(f, x))
        
        assert (self.parser.parse('f:obj->obj(g:obj->obj(x))')
                == qterm.unary_op(f, qterm.unary_op(g, x)))

        assert (self.parser.parse('h:obj->obj->obj(x, y)')
                == qterm.binary_op(h, x, y))

    def test_parse_abstraction(self):
        f = qterm.Variable('f', qfun(qbool(), qbool()))
        x = qterm.Variable('x', qbool())
        y = qterm.Variable('y', qbool())
        
        assert (self.parser.parse(r'\x:bool x')
                == qterm.Abstraction(x, x))

        assert (self.parser.parse(r'\x:bool \y:bool x')
                == qterm.Abstraction(x, qterm.Abstraction(y, x)))
        
        assert (self.parser.parse(r'\x f:bool->bool(x)')
                == qterm.Abstraction(x, qterm.unary_op(f, x)))

    def test_prefix_constant(self):
        assert self.parser.parse('(exists)') == self.exists
        assert self.parser.parse('(=)') == self.equals
        self.parser.parse(r'(exists) = (\x.(not (for_all y . (not x(y)))))')
