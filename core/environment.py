import os.path

from cheqed.core import parser, printer, qterm, qtype, syntax, sequent, unification
from cheqed.core import trace
from cheqed.core.match import match_term
from cheqed.core.qterm import is_term
from cheqed.core.term_type_unifier import unify_types

def arg_types(*args):
    def assign_types(rule):
        rule.arg_types = args
        return rule
    return assign_types

def make_is_applicable(predicate):
    def is_applicable(goal):
        try:
            return predicate(goal)
        except:
            return False
    return is_applicable

def applicable(predicate):
    def assign_predicate(rule):
        rule.is_applicable = make_is_applicable(predicate)
        return rule
    return assign_predicate

class RuleBuilder:
    def __init__(self, environment, rule, factory):
        self.environment = environment
        self.rule = rule
        self.factory = factory

    def __call__(self, *args):
        args = self.environment.parse_args(self.rule, args)
        return self.factory(self.rule, *args)

    def rule_name(self):
        return self.rule.func_name

    def arg_types(self):
        try:
            return self.rule.arg_types
        except AttributeError:
            return []

    def is_applicable(self, goal):
        try:
            return self.rule.is_applicable(goal)
        except AttributeError:
            pass
        
        if self.arg_types():
            return True

        try:
            self().evaluate(goal)
            return True
        except Exception, e:
            return False

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
            'applicable': applicable,
            'arg_types': arg_types,
            'match': self.match,

            'sequent': sequent.Sequent,

            'substitute': qterm.substitute,
            'free_variables': qterm.free_variables,

            'is_constant': qterm.is_constant,
            'is_variable': qterm.is_variable,
            'is_combination': qterm.is_combination,
            'is_abstraction': qterm.is_abstraction,
            
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
        self.add_primitive(self.theorem)
        self.add_compound(self.theorem_cut)        

    def add_type(self, type_):
        self.types.append(type_)
        self.parser = None

    def add_constant(self, constant):
        atom = self.parse(constant)
        if qterm.is_variable(atom):
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
        assert qterm.is_combination(term)
        assert qterm.is_combination(term.operator)
        assert term.operator.operator.name == '='
        assert qterm.is_variable(term.operator.operand) \
            or qterm.is_constant(term.operator.operand)
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
            if is_term(arg):
                return arg
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
            return repr(self.printer.print_term(arg))
        else:
            raise Exception('unrecognized arg_type %r' % arg_type)

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
            rule = self.print_proof(proof.rule)
            branches = [self.print_proof(branch) for branch in proof.branches]
            return 'branch(%s)' % (', '.join([rule] + branches))
        else:
            raise Exception('unrecognized proof type %r' % proof)

    def add_primitive(self, rule):
        builder = RuleBuilder(self, rule, trace.Primitive)
        self.rules[builder.rule_name()] = builder
        return builder

    def add_compound(self, rule):
        builder = RuleBuilder(self, rule, trace.Compound)
        self.rules[builder.rule_name()] = builder
        return builder

    def _make_scope(self):
        scope = globals().copy()
        scope.update(self.helpers)
        scope.update(self.rules)
        return scope        
    
    def load_extension(self, extension):
        exec extension in self._make_scope()

    def evaluate(self, text):
        return eval(text, self._make_scope())
        
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

    def applicable_rules(self, goal):
        return [builder for builder in self.rules.values()
                if builder.is_applicable(goal)]

    def match(self, term, string):
        pattern = self.parse(string)
        return match_term(pattern, term)

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

    def theorem(self, goal):
        term = goal.right[0]
        for thm in self.axioms.itervalues():
            if thm == term:
                return []
        raise Exception('theorem does not apply')

    @arg_types('str')
    def theorem_cut(self, goal, name):
        branch = trace.branch
        cut = self.rules['cut']
        theorem = self.rules['theorem']
        noop = self.rules['noop']
        return branch(cut(self.axioms[name]),
                      theorem(),
                      noop())
    
def expand_definition(term, definition):
    atom, value = definition.operator.operand, definition.operand
    atom, term = unify_types([atom, term])
    return qterm.substitute(term, value, atom)

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

def make_default():
    env = load_modules('logic', 'set')
    env.load_extension(open('/home/cap/thesis/cheqed/core/rules/structure.py'))
    env.load_extension(open('/home/cap/thesis/cheqed/core/rules/logic_primitive.py'))
    env.load_extension(open('/home/cap/thesis/cheqed/core/rules/logic_compound.py'))
    env.load_extension(open('/home/cap/thesis/cheqed/core/rules/set.py'))
    return env
