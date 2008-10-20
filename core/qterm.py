import re

from cheqed.core.unification import Unifier, UnificationError
from cheqed.core import qtype, unification

class Term(object):
    @property
    def role(self):
        return self._role

    @property
    def is_constant(self):
        return self.role == 'constant'

    @property
    def is_variable(self):
        return self.role == 'variable'

    @property
    def is_combination(self):
        return self.role == 'combination'

    @property
    def is_abstraction(self):
        return self.role == 'abstraction'

def make_atom_unifier(atom, other, unifier=None):
    if unifier is None:
        unifier = Unifier()

    if hasattr(other, 'name'):
        if (atom.name == other.name
            or atom.name == '='):
            return unifier

    if atom.is_variable:
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

    if term.is_constant or term.is_variable:
        return make_atom_unifier(term, other, unifier)
        
    if other.is_constant or other.is_variable:
        return make_atom_unifier(other, term, unifier)
    
    if term.is_combination and other.is_combination:
        unifier = make_unifier(term.operator, other.operator, unifier)
        unifier = make_unifier(term.operand, other.operand, unifier)
        return unifier

    if term.is_abstraction and other.is_abstraction:
        unifier = make_unifier(term.bound, other.bound, unifier)
        unifier = make_unifier(term.body, other.body, unifier)
        return unifier

    raise UnificationError('Cannot unify %s with %s'
                                       % (term, other))

def unify(term, other):
    unifier = make_unifier(term, other)
    for key, value in unifier.unified_subs().iteritems():
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

def match(pattern, term, assignments=None):
    if assignments is None:
        assignments = {}

    if pattern.is_variable and types_unify([pattern.qtype, term.qtype]):
        if pattern.name in assignments:
            if assignments[pattern.name] == term:
                return assignments
            raise UnificationError('Cannot match %s with both %s and %s.'
                                   % (pattern, term,
                                      assignments[pattern.name]))
        assignments[pattern.name] = term
        return assignments

    if pattern.is_constant and term.is_constant:
        if (pattern.name == term.name
            and types_unify([pattern.qtype, term.qtype])):
            return assignments
        raise UnificationError('Cannot match %s with %s.' % (pattern, term))

    if pattern.is_combination and term.is_combination:
        assignments = match(pattern.operator, term.operator, assignments)
        assignments = match(pattern.operand, term.operand, assignments)
        return assignments

    if pattern.is_abstraction and term.is_abstraction:
        assignments = match(pattern.bound, term.bound, assignments)
        assignments = match(pattern.body, term.body, assignments)
        return assignments

    raise UnificationError('Cannot match %s with %s.' % (pattern, term))

def make_type_unifier(terms, unifier=None):
    if unifier is None:
        unifier = unification.Unifier()
        
    atoms_by_name = {}
    for term in terms:
        for atom in term.free_variables:
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
    _role = 'constant'
    
    def __init__(self, name, qtype_):
        self._name = name
        self._qtype = qtype_
        
    @property
    def name(self):
        return self._name

    @property
    def qtype(self):
        return self._qtype

    @property
    def free_variables(self):
        return set()

    @property
    def variables(self):
        return set([self])
    
    def substitute(self, a, b, respect_bound=True):
        if self == b:
            return a
        else:
            return self

    def substitute_type(self, a, b):
        qtype = self.qtype.substitute(a, b)
        return Constant(self.name, qtype)

    def unify(self, other):
        return unify(self, other)
    
    def __repr__(self):
        return 'Constant(%s, %s)' % (self.name, repr(self.qtype))

    def __eq__(self, other):
        return (self.role == other.role
                and self.name == other.name
                and self.qtype == other.qtype)

    def __ne__(self, other):
        return not self == other
    
class Variable(Term):
    _role = 'variable'
    
    def __init__(self, name, qtype_):
        self._name = name
        self._qtype = qtype_

    @property
    def name(self):
        return self._name

    @property
    def qtype(self):
        return self._qtype

    @property
    def free_variables(self):
        return set([self])

    @property
    def variables(self):
        return set([self])

    def substitute(self, a, b, respect_bound=True):
        if self == b:
            return a
        else:
            return self

    def substitute_type(self, a, b):
        qtype = self.qtype.substitute(a, b)
        return Variable(self.name, qtype)

    def unify(self, other):
        return unify(self, other)
    
    def __repr__(self):
        return 'Variable(%s, %s)' % (self.name, repr(self.qtype))
    
    def __eq__(self, other):
        return (self.role == other.role
                and self.name == other.name
                and self.qtype == other.qtype)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.role) ^ hash(self.name) ^ hash(self.qtype)

class Combination(Term):
    _role = 'combination'

    def beta_reduce(self):
        if self.operator.is_abstraction:
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
        self._operator, self._operand = self.infer_types(operator, operand)

    @property
    def operator(self):
        return self._operator
    
    @property
    def operand(self):
        return self._operand

    @property
    def qtype(self):
        return self.operator.qtype.args[1]

    @property
    def free_variables(self):
        return self.operator.free_variables | self.operand.free_variables

    @property
    def variables(self):
        return self.operator.variables | self.operand.variables
    
    def substitute(self, a, b, respect_bound=True):
        return Combination(self.operator.substitute(a, b, respect_bound),
                           self.operand.substitute(a, b, respect_bound)).beta_reduce()

    def substitute_type(self, a, b):
        return Combination(self.operator.substitute_type(a, b),
                           self.operand.substitute_type(a, b))

    def unify(self, other):
        return unify(self, other)
    
    def __repr__(self):
        return 'Combination(%s, %s)' % (repr(self.operator),
                                        repr(self.operand))
    
    def __eq__(self, other):
        return (self.role == other.role
                and self.operator == other.operator
                and self.operand == other.operand)

    def __ne__(self, other):
        return not self == other

class Abstraction(Term):
    _role = 'abstraction'

    @staticmethod
    def infer_types(bound, body):
        return unify_types([bound, body])
    
    def __init__(self, bound, body):
        self._bound, self._body = self.infer_types(bound, body)
        
        if self._bound.role != 'variable':
            raise qtype.UnificationError('Bound terms must be variables.')

    @property
    def bound(self):
        return self._bound

    @property
    def body(self):
        return self._body

    @property
    def qtype(self):
        return qtype.qfun(self.bound.qtype, self.body.qtype)

    @property
    def free_variables(self):
        return self.body.free_variables - set([self.bound])

    @property
    def variables(self):
        return self.body.variables | set([self.bound])
    
    def substitute(self, a, b, respect_bound=True):
        if respect_bound:
            if self.bound in b.free_variables:
                return self

            bound = self.bound
            body = self.body
            a_names = set([var.name for var in a.free_variables])
            if bound.name in a_names:
                names = set([var.name for var in body.variables]) \
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

    def unify(self, other):
        return unify(self, other)
    
    def __repr__(self):
        return 'Abstraction(%s, %s)' % (repr(self.bound), repr(self.body))

    def __eq__(self, other):
        return (self.role == other.role
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
