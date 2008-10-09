import os.path

from cheqed.core import parser, printer, qterm, qtype, syntax, sequent, plan
from cheqed.core import trace

def arg_types(*args):
    def assign_types(rule):
        rule.arg_types = args
        return rule
    return assign_types

class Environment:
    def __init__(self):
        self.constants = {}
        self.definitions = {}
        self.axioms = {}
        self.operators = []
        self.binders = []
        self.types = []
        self.parser = None
        self.printer = None

        self.rules = {}
        self.helpers = {
            'arg_types': arg_types,
            'match': self.match,

            'sequent': sequent.Sequent,
            
            'primitive': self.add_primitive,
            'compound': self.add_compound,
            'branch': trace.branch,
            'sequence': trace.sequence,

            'constant': self.add_constant,
            'axiom': self.add_axiom,
            'definition': self.add_definition,
            'operator': self.add_operator,
            'binder': self.add_binder,
            }

        self.add_primitive(self.left_expand)
        self.add_primitive(self.right_expand)
        
        self.plans = {}
        self.plans['assumption'] = plan.assumption
        self.plans['branch'] = plan.branch
        self.plans['parse'] = self.parse

    def add_type(self, type_):
        self.types.append(type_)
        self.parser = None

    def add_constant(self, constant):
        atom = self.parse(constant)
        if atom.is_variable:
            atom = qterm.Constant(atom.name, atom.qtype)
        self.constants[atom.name] = atom

    def add_operator(self, name, arity, associativity, precedence):
        self.operators.append(
            syntax.Operator(self.constants[name], arity, associativity, precedence))
        self.parser = None

    def add_binder(self, name):
        self.binders.append(syntax.Binder(self.constants[name]))
        self.parser = None

    def add_definition(self, string):
        term = self.parse(string)
        assert term.is_combination
        assert term.operator.is_combination
        assert term.operator.operator.name == '='
        assert term.operator.operand.is_variable \
            or term.operator.operand.is_constant
        name = term.operator.operand.name
        self.definitions[name] = term

    def add_axiom(self, name, string):
        self.axioms[name] = self.parse(string)

    def parse_arg(self, arg_type, arg):
        if arg_type == 'int':
            return int(arg)
        elif arg_type == 'str':
            return str(arg)
        elif arg_type == 'term':
            return self.parse(arg)
        else:
            raise Exception('unrecognized arg_type')
        
    def parse_args(self, rule, args):
        try:
            return [self.parse_arg(t, a) for t, a in zip(rule.arg_types, args)]
        except AttributeError:
            pass
        return args

    def print_arg(self, arg_type, arg):
        if arg_type == 'int':
            return str(arg)
        elif arg_type == 'str':
            return repr(arg)
        elif arg_type == 'term':
            return repr(self.printer.term(arg))
        else:
            raise Exception('unrecognized arg_type')

    def print_args(self, rule, args):
        try:
            return [self.print_arg(t, a) for t, a in zip(rule.arg_types, args)]
        except AttributeError:
            pass
        return args
        
    def print_proof(self, proof):
        if isinstance(proof, (trace.Primitive, trace.Compound)):
            args = self.print_args(proof.func, proof.args)
            return '%s(%s)' % (proof.func.func_name,
                               ', '.join(args))
        elif isinstance(proof, trace.Branch):
            branches = [self.print_proof(branch) for branch in proof.branches]
            return 'branch(%s, %s)' % (self.print_proof(proof.rule),
                                       ', '.join(branches))
        else:
            raise Exception('unrecognized arg_type')

    def _make_primitive(self, rule):
        def _make(*args):
            args = self.parse_args(rule, args)
            return trace.Primitive(rule, *args)
        return _make
    
    def add_primitive(self, rule):
        make = self._make_primitive(rule)
        self.rules[rule.func_name] = make
        return make

    def _make_compound(self, rule):
        def _make(*args):
            args = self.parse_args(rule, args)
            return trace.Compound(rule, *args)
        return _make

    def add_compound(self, rule):
        make = self._make_compound(rule)
        self.rules[rule.func_name] = make
        return make

    def load_extension(self, extension):
        scope = globals().copy()
        scope.update(self.helpers)
        scope.update(self.rules)
        exec extension in scope

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

    def make_parser(self):
        extensions = self.types + self.operators + self.binders
        self.parser = parser.Parser(syntax.Syntax(extensions))

    def make_printer(self):
        extensions = self.types + self.operators + self.binders
        self.printer = printer.Printer(syntax.Syntax(extensions))

    def parse(self, string):
        if self.parser is None:
            self.make_parser()
        return self.parser.parse(string)

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

    def match(self, term, string):
        pattern = self.parse(string)
        return qterm.match(pattern, term)

    @arg_types('str')
    def left_expand(self, goal, name):
        definition = self.definitions[name]
        return [sequent.Sequent(([expand_definition(goal.left[0],
                                                    definition)]
                                 + goal.left[1:]),
                                goal.right)]

    @arg_types('str')
    def right_expand(self, goal, name):
        definition = self.definitions[name]
        return [sequent.Sequent(goal.left,
                                ([expand_definition(goal.right[0],
                                                    definition)]
                                 + goal.right[1:]))]


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



theory_root = '/home/cap/thesis/cheqed/core/theory'
def load_modules(*modules):
    env = Environment()
    env.add_type(syntax.Type(qtype.qobj, 'obj'))
    env.add_type(syntax.Type(qtype.qbool, 'bool'))

    extensions = [open(os.path.join(theory_root, '%s.py' % module))
                  for module in modules]

    for extension in extensions:
        env.load_extension(extension)

    env.make_printer()
    return env
