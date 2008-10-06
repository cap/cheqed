import os.path

from cheqed.core import parser, printer, qterm, qtype, syntax

class Configuration(object):
    def __init__(self, constants, definitions, axioms, operators, binders):
        self.constants = constants
        self.definitions = definitions
        self.axioms = axioms
        self.operators = operators
        self.binders = binders

    def update(self, other):
        self.constants.extend(other.constants)
        self.definitions.extend(other.definitions)
        self.axioms.update(other.axioms)
        self.operators.extend(other.operators)
        self.binders.extend(other.binders)

    def make_environment(self):
        extensions = [syntax.Type(qtype.qobj, 'obj'),
                      syntax.Type(qtype.qbool, 'bool')]

        bootstrap_parser = parser.Parser(syntax.Syntax(extensions))

        constants = {}
        for constant in self.constants:
            atom = bootstrap_parser.parse(constant)
            if atom.is_variable:
                atom = qterm.Constant(atom.name, atom.qtype)
            constants[atom.name] = atom

        extensions.extend(
            [syntax.Operator(constants[name], arity, associativity, precedence)
             for name, arity, associativity, precedence in self.operators])

        extensions.extend(
            [syntax.Binder(constants[name]) for name in self.binders])

        real_parser = parser.Parser(syntax.Syntax(extensions))

        definitions = {}
        for string in self.definitions:
            term = real_parser.parse(string)
            assert term.is_combination
            assert term.operator.is_combination
            assert term.operator.operator.name == '='
            assert term.operator.operand.is_variable \
                or term.operator.operand.is_constant
            name = term.operator.operand.name
            definitions[name] = term

        axioms = {}
        for name, string in self.axioms.iteritems():
            axioms[name] = real_parser.parse(string)

        printer_ = printer.Printer(syntax.Syntax(extensions))
            
        return Environment(real_parser, printer_,
                           constants, definitions, axioms)
        
class Environment(object):
    def __init__(self, parser, printer, constants, definitions, axioms):
        self.parser = parser
        self.printer = printer
        self.constants = constants
        self.definitions = definitions
        self.axioms = axioms

def _load_single(expr):
    constants = []
    def constant(string):
        constants.append(string)

    definitions = []
    def definition(string):
        definitions.append(string)

    axioms = {}
    def axiom(name, string):
        axioms[name] = string
        
    operators = []
    def operator(name, arity, associativity, precedence):
        operators.append((name, arity, associativity, precedence))

    binders = []
    def binder(name):
        binders.append(name)

    scope = {
        'constant': constant,
        'axiom': axiom,
        'definition': definition,
        'operator': operator,
        'binder': binder,
        }
    scope.update(globals())    

    exec expr in scope

    return Configuration(constants, definitions, axioms, operators, binders)

def _load(expr):
    conf = Configuration([], [], {}, [], [])
    for module in expr:
        conf.update(_load_single(module))
    return conf

theory_root = '/home/cap/thesis/cheqed/core/theory'
_cache = {}
def load_modules(*modules):
    if modules in _cache:
        return _cache[modules]
    
    files = [open(os.path.join(theory_root, '%s.py' % module))
             for module in modules]
    conf = _load(files)
    env = conf.make_environment()
    _cache[modules] = env
    return env
