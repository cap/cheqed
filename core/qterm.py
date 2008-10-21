from cheqed.core.unification import Unifier, UnificationError
from cheqed.core import qtype, unification

def is_constant(term): return isinstance(term, Constant)
def is_variable(term): return isinstance(term, Variable)
def is_combination(term): return isinstance(term, Combination)
def is_abstraction(term): return isinstance(term, Abstraction)
def is_atom(term): return is_constant(term) or is_variable(term)

def free_variables(term):
    if is_constant(term):
        return set()
    elif is_variable(term):
        return set([term])
    elif is_combination(term):
        return free_variables(term.operator) | free_variables(term.operand)
    elif is_abstraction(term):
        return free_variables(term.body) - set([term.bound])

def atoms(term):
    if is_atom(term):
        return set([term])
    elif is_combination(term):
        return atoms(term.operator) | atoms(term.operand)
    elif is_abstraction(term):
        return atoms(term.body) | set([term.bound])

class Term(object):
    pass

def make_atom_unifier(atom, other, unifier=None):
    if unifier is None:
        unifier = Unifier()

    if hasattr(other, 'name'):
        if (atom.name == other.name
            or atom.name == '='):
            return unifier

    if is_variable(atom):
        try:
            qtype.unify([atom.qtype, other.qtype])
        except UnificationError, ue:
            raise UnificationError('Cannot unify %s with %s.' % (atom, other))
#        atom.qtype.unify(other.qtype)
        unifier.add_subs(atom, other)
        return unifier

    raise UnificationError('Cannot unify %s with %s' % (atom, other))

def make_unifier(term, other, unifier=None):
    if unifier is None:
        unifier = Unifier()

    if is_constant(term) or is_variable(term):
        return make_atom_unifier(term, other, unifier)
        
    if is_constant(other) or is_variable(other):
        return make_atom_unifier(other, term, unifier)
    
    if is_combination(term) and is_combination(other):
        unifier = make_unifier(term.operator, other.operator, unifier)
        unifier = make_unifier(term.operand, other.operand, unifier)
        return unifier

    if is_abstraction(term) and is_abstraction(other):
        unifier = make_unifier(term.bound, other.bound, unifier)
        unifier = make_unifier(term.body, other.body, unifier)
        return unifier

    raise UnificationError('Cannot unify %s with %s'
                                       % (term, other))

def unify(term, other):
    unifier = make_unifier(term, other)
    for key, value in unifier.unified_subs(is_variable, atoms).iteritems():
        term = term.substitute(value, key, respect_bound=False)
        other = other.substitute(value, key, respect_bound=False)

    term, other = unify_types([term, other])

    if term != other:
        raise UnificationError('Cannot unify %s with %s'
                                           % (term, other))

    return term

from cheqed.core.unification import UnificationError

def types_unify(types):
    try:
        qtype.unify(types)
        return True
    except UnificationError:
        return False

def make_type_unifier(terms, unifier=None):
    if unifier is None:
        unifier = unification.Unifier()
        
    atoms_by_name = {}
    for term in terms:
        for atom in free_variables(term):
            if atom.name != '=':
                atoms_by_name.setdefault(atom.name, []).append(atom)

    unifier = qtype.Unifier()
    for name, atoms in atoms_by_name.iteritems():
        if len(atoms) > 1:
            try:
                unifier = qtype.make_unifier([atom.qtype for atom in atoms],
                                             unifier)
            except unification.UnificationError:
                raise unification.UnificationError('Cannot unify types for atoms %s.' % ' and '.join([str(atom) for atom in atoms]))

    return unifier
    
def unify_types(terms):
    unifier = make_type_unifier(terms)

    for key, value in unifier.unified_subs().iteritems():
        for i in range(len(terms)):
            terms[i] = terms[i].substitute_type(value, key)

    return terms

class Constant(Term):
    def __init__(self, name, qtype_):
        self.name = name
        self.qtype = qtype_

    def substitute(self, a, b, respect_bound=True):
        if self == b:
            return a
        else:
            return self

    def substitute_type(self, a, b):
        qtype = self.qtype.substitute(a, b)
        return Constant(self.name, qtype)

    def __repr__(self):
        return 'Constant(%r, %r)' % (self.name, self.qtype)

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.name == other.name
                and self.qtype == other.qtype)

    def __ne__(self, other):
        return not self == other
    
class Variable(Term):
    def __init__(self, name, qtype_):
        self.name = name
        self.qtype = qtype_

    def substitute(self, a, b, respect_bound=True):
        if self == b:
            return a
        else:
            return self

    def substitute_type(self, a, b):
        qtype = self.qtype.substitute(a, b)
        return Variable(self.name, qtype)

    def __repr__(self):
        return 'Variable(%r, %r)' % (self.name, self.qtype)
    
    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.name == other.name
                and self.qtype == other.qtype)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.__class__) ^ hash(self.name) ^ hash(self.qtype)

class Combination(Term):
    def beta_reduce(self):
        if is_abstraction(self.operator):
            return self.operator.body.substitute(self.operand,
                                                 self.operator.bound)
        return self

    @staticmethod
    def infer_types(operator, operand):
        if operator.qtype.is_variable:
            operator = operator.substitute_type(qtype.qfun(qtype.qvar(),
                                                           qtype.qvar()),
                                                operator.qtype)

        if operator.qtype.name != 'fun':
            raise qtype.UnificationError('Operators must be functions.')
        
        unifier = qtype.make_unifier([operator.qtype.args[0], operand.qtype])
        for key, value in unifier.unified_subs().iteritems():
            operator = operator.substitute_type(value, key)
            operand = operand.substitute_type(value, key)

        operator, operand = unify_types([operator, operand])
        
        if operator.qtype.args[0] != operand.qtype:
            message = ('Combination operand type must match'
                       ' operator argument type. Operand %r does not match'
                       ' operator %r.' % (operand, operator))
            raise qtype.UnificationError(message)

        return operator, operand
        
    def __init__(self, operator, operand):
        self.operator, self.operand = self.infer_types(operator, operand)

    @property
    def qtype(self):
        return self.operator.qtype.args[1]
    
    def substitute(self, a, b, respect_bound=True):
        return Combination(self.operator.substitute(a, b, respect_bound),
                           self.operand.substitute(a, b, respect_bound)).beta_reduce()

    def substitute_type(self, a, b):
        return Combination(self.operator.substitute_type(a, b),
                           self.operand.substitute_type(a, b))

    def __repr__(self):
        return 'Combination(%r, %r)' % (self.operator, self.operand)
    
    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.operator == other.operator
                and self.operand == other.operand)

    def __ne__(self, other):
        return not self == other

class Abstraction(Term):
    @staticmethod
    def infer_types(bound, body):
        return unify_types([bound, body])
    
    def __init__(self, bound, body):
        self.bound, self.body = self.infer_types(bound, body)
        
        if not is_variable(self.bound):
            raise qtype.UnificationError('Bound terms must be variables.')

    @property
    def qtype(self):
        return qtype.qfun(self.bound.qtype, self.body.qtype)
    
    def substitute(self, a, b, respect_bound=True):
        if respect_bound:
            if self.bound in free_variables(b):
                return self

            bound = self.bound
            body = self.body
            a_names = set([var.name for var in free_variables(a)])
            if bound.name in a_names:
                names = set([var.name for var in atoms(body)]) \
                        | a_names
                new_name = bound.name
                i = 1
                while new_name in names:
                    new_name = bound.name + str(i)
                    i += 1
                new_bound = Variable(new_name, bound.qtype)
                body = body.substitute(new_bound, bound)
                bound = new_bound
                
            return Abstraction(bound,
                               body.substitute(a, b, respect_bound))
        else:
            return Abstraction(self.bound.substitute(a, b, respect_bound),
                               self.body.substitute(a, b, respect_bound))

    def substitute_type(self, a, b):
        return Abstraction(self.bound.substitute_type(a, b),
                           self.body.substitute_type(a, b))

    
    def __repr__(self):
        return 'Abstraction(%r, %r)' % (self.bound, self.body)

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.bound == other.bound
                and self.body == other.body)

    def __ne__(self, other):
        return not self == other

def unary_op(op, a):
    return Combination(op, a)

def binary_op(op, a, b):
    return Combination(Combination(op, a), b)

def binder(op, x, a):
    return unary_op(op, Abstraction(x, a))
