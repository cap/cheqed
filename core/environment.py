import os.path

from cheqed.core import parser, printer, qterm, qtype, syntax, sequent, plan
from cheqed.core.rules.registry import register, make_compound, applicable

class Configuration(object):
    def __init__(self):
        self.constants = {}
        self.definitions = {}
        self.axioms = {}
        self.operators = []
        self.binders = []
        self.types = []
        self.parser = None
        self.printer = None

    def add_type(self, type_):
        self.types.append(type_)
        self.make_parser()

    def add_constant(self, constant):
        atom = self.parser.parse(constant)
        if atom.is_variable:
            atom = qterm.Constant(atom.name, atom.qtype)
        self.constants[atom.name] = atom

    def add_operator(self, name, arity, associativity, precedence):
        self.operators.append(
            syntax.Operator(self.constants[name], arity, associativity, precedence))
        self.make_parser()

    def add_binder(self, name):
        self.binders.append(syntax.Binder(self.constants[name]))
        self.make_parser()

    def add_definition(self, string):
        term = self.parser.parse(string)
        assert term.is_combination
        assert term.operator.is_combination
        assert term.operator.operator.name == '='
        assert term.operator.operand.is_variable \
            or term.operator.operand.is_constant
        name = term.operator.operand.name
        self.definitions[name] = term

    def add_axiom(self, name, string):
        self.axioms[name] = self.parser.parse(string)
        
    def make_parser(self):
        extensions = self.types + self.operators + self.binders
        self.parser = parser.Parser(syntax.Syntax(extensions))

    def make_printer(self):
        extensions = self.types + self.operators + self.binders
        self.printer = printer.Printer(syntax.Syntax(extensions))
        
    def update(self, other):
        self.constants.extend(other.constants)
        self.definitions.extend(other.definitions)
        self.axioms.update(other.axioms)
        self.operators.extend(other.operators)
        self.binders.extend(other.binders)
        
    def make_environment(self):
        self.make_parser()
        self.make_printer()
        
        return Environment(self.parser, self.printer,
                           self.constants, self.definitions, self.axioms)

    
class Environment(object):
    def __init__(self, parser, printer, constants, definitions, axioms):
        self.parser = parser
        self.printer = printer
        self.constants = constants
        self.definitions = definitions
        self.axioms = axioms
        self.plans = {}
        
        self.plans['assumption'] = plan.assumption
        self.plans['branch'] = plan.branch
        self.plans['parse'] = self.parser.parse

    def set_up(self):
        self.load_plan('rules.structural')
        self.load_plan('rules.logical')
        
#        self.register(self.left_expand)
#        self.register(self.right_expand)
#        self.register(self.theorem)
#        self.register(self.theorem_cut)

    def load_plan(self, plan):
        mod = __import__(plan)
        components = plan.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        for name in dir(mod):
            rule = getattr(mod, name)
            try:
                if rule.is_registered == True:
                    self.plans[rule.func_name] = rule
            except AttributeError:
                pass

    def is_applicable(self, func, goal):
        if hasattr(func, 'is_applicable'):
            return func.is_applicable(self, goal)

        if not hasattr(func, 'arg_names'):
            return False        
        if len(func.arg_names) > 0:
            return True

        try:
            tester = func()
            tester.subgoals(goal)
        except Exception, e:
            return False

        return True

    def applicable_rules(self, goal):
        applicable = []
        for name, func in self.plans.items():
            if self.is_applicable(func, goal):
                applicable.append((func.func_name, func.arg_names))

        return applicable
            
    def evaluate(self, text):
        return eval(text, globals(), self.plans)

    @staticmethod
    def decorate(plan):
        arg_names, varargs, varkw, defaults = inspect.getargspec(func)

        if not hasattr(func, 'arg_names'):
            func.arg_names = arg_names
        
    def register(self, plan):
        self.decorate(plan)
        self.plans.append(plan)

    def match_first(sequent, side, string):
        term = sequent[side][0]
        pattern = self.parser.parse(string)
        return qterm.match(pattern, term)

    def match_second(sequent, side, string):
        term = sequent[side][1]
        pattern = self.parser.parse(string)
        return qterm.match(pattern, term)

        
#     def left_expand(self, name):
#         return rule(lambda x: _left_expand(x, self.definitions[name]),
#                     'left_expand(%r)' % name)

#     def right_expand(self, name):
#         return rule(lambda x: _right_expand(x, self.definitions[name]),
#                     'right_expand(%r)' % name)

#     def _theorem(self, sequent):
#         term = sequent.right[0]
#         for thm in env.axioms.itervalues():
#             if thm == term:
#                 return []
#         raise unification.UnificationError('theorem does not apply.')

#     def theorem(self):
#         return rule(_theorem, 'theorem()')

#     @make_compound
#     def theorem_cut(self, goal, name):
#         return branch(cut(self.axioms[name]),
#                       theorem(),
#                       assumption())
    
def expand_definition(term, definition):
    atom, value = definition.operator.operand, definition.operand
    return term.substitute(value, atom)                    

def _left_expand(sequent, definition):
    return [sequent.Sequent(([expand_definition(sequent.left[0], definition)]
                     + sequent.left[1:]),
                    sequent.right)]

def _right_expand(sequent, definition):
    return [sequent.Sequent(sequent.left,
                    ([expand_definition(sequent.right[0], definition)]
                     + sequent.right[1:]))]

    

def _load_single(conf, expr):
    scope = {
        'constant': conf.add_constant,
        'axiom': conf.add_axiom,
        'definition': conf.add_definition,
        'operator': conf.add_operator,
        'binder': conf.add_binder,
        }
    scope.update(globals())    

    exec expr in scope

def _load(expr):
    conf = Configuration()
    conf.add_type(syntax.Type(qtype.qobj, 'obj'))
    conf.add_type(syntax.Type(qtype.qbool, 'bool'))
    conf.add_type(syntax.Type(qtype.qunit, 'unit'))
    conf.add_type(syntax.Type(qtype.qint, 'int'))
    conf.make_parser()
    
    for module in expr:
        _load_single(conf, module)
        conf.make_parser()
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
