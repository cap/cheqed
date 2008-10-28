'''Represent terms from the typed lambda calculus.

I've gone back and forth about how to structure the
representation. Should terms be large objects, with methods to query
for free variables and perform substutions? Or should they be very
small value types, with free methods acting upon them?

Large Objects
-------------

Can be consistent with other types of objects: foo.free_variables()
can work whether foo is a term or a sequent.

Much of the type dispatching we need in small objects is taken care of
by the object system.

Small Objects
-------------

Better code organization: we more often want to think in terms of
methods rather than objects.


Furthermore, what do we do about correctness? It seems a bit heavy to
do typechecking and inference at construction time. Maybe we just do a
check, then move inference elsewhere when it is needed?

Although, really, what sort of correctness do we want to guarantee?
And in what scope? Do we want all variables with the same name to have
the same type? All variables in the same scope with the same name ... ?

Up to this point, we have, in an ad-hoc way, forced all variables with
the same name in a particular sequent to have the same
type. Introducing a new instance of an existing variable with the
wrong type leads to a unification error. That said, introducing a new
instance of an existing variable with a variable type causes type
inference to assign a type to that variable, insofar as its type can
be inferred.


'''

from cheqed.core.unification import Unifier, UnificationError
from cheqed.core import qtype, unification
from cheqed.core.qtype_unifier import TypeUnifier

def is_constant(term):
    return isinstance(term, Constant)

def is_variable(term):
    return isinstance(term, Variable)

def is_combination(term):
    return isinstance(term, Combination)

def is_abstraction(term):
    return isinstance(term, Abstraction)

def is_atom(term):
    return isinstance(term, Atom)

def is_term(term):
    return is_atom(term) or is_combination(term) or is_abstraction(term)

def by_name(atoms):
    by_name = {}
    for atom in atoms:
        by_name.setdefault(atom.name, []).append(atom)
    return by_name
    
def validate_substitution(a, b):
    return
    if a.qtype != b.qtype:
        raise TypeError('cannot substitute term of type %s for term of type %s'
                        % (a.qtype, b.qtype))

def substitute(term, a, b):
    '''Substitute a for b in term, respecting bound variables.'''
    validate_substitution(a, b)
    
    if is_atom(term):
        if term == b:
            return a
        else:
            return term
    elif is_combination(term):
        return beta_reduce(Combination(substitute(term.operator, a, b),
                                       substitute(term.operand, a, b)))
    elif is_abstraction(term):
        if term.bound in b.free_variables():
            return term
        bound = term.bound
        body = term.body
        a_names = set([var.name for var in a.free_variables()])
        if bound.name in a_names:
            names = set([var.name for var in body.atoms()]) \
                | a_names
            new_name = bound.name
            i = 1
            while new_name in names:
                new_name = bound.name + str(i)
                i += 1
            new_bound = Variable(new_name, bound.qtype)
            body = substitute(body, new_bound, bound)
            bound = new_bound
        return Abstraction(bound, substitute(body, a, b))

def substitute_type(term, a, b):
    if is_constant(term):
        qtype = term.qtype.substitute(a, b)
        return Constant(term.name, qtype)
    elif is_variable(term):
        qtype = term.qtype.substitute(a, b)
        return Variable(term.name, qtype)
    elif is_combination(term):
        return Combination(substitute_type(term.operator, a, b),
                           substitute_type(term.operand, a, b))    
    elif is_abstraction(term):
        return Abstraction(substitute_type(term.bound, a, b),
                           substitute_type(term.body, a, b))

from cheqed.core.unification import UnificationError

def types_unify(types):
    unifier = TypeUnifier()
    try:
        unifier.unify_many(types)
    except UnificationError:
        return False
    return True

def beta_reduce(term):
    if not is_combination(term):
        return term
    
    if is_abstraction(term.operator):
        return substitute(term.operator.body,
                          term.operand,
                          term.operator.bound)
    return term


class Atom(object):
    def __init__(self, name, qtype_):
        self._name = name
        self._qtype = qtype_

    @property
    def name(self):
        return self._name

    @property
    def qtype(self):
        return self._qtype

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.name == other.name
                and self.qtype == other.qtype)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.__class__) ^ hash(self.name) ^ hash(self.qtype)

    def atoms(self):
        return set([self])


class Constant(Atom):
    def __repr__(self):
        return 'Constant(%r, %r)' % (self.name, self.qtype)
    
    def free_variables(self):
        return set()


class Variable(Atom):
    def __repr__(self):
        return 'Variable(%r, %r)' % (self.name, self.qtype)

    def free_variables(self):
        return set([self])


class Combination(object):
    def __init__(self, operator, operand):
        self._operator = operator
        self._operand = operand

    @property
    def operator(self):
        return self._operator

    @property
    def operand(self):
        return self._operand
        
    @property
    def qtype(self):
        return self.operator.qtype.args[1]
    
    def __repr__(self):
        return 'Combination(%r, %r)' % (self.operator, self.operand)
    
    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.operator == other.operator
                and self.operand == other.operand)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.__class__) ^ hash(self.operator) ^ hash(self.operand)

    def atoms(self):
        return self.operator.atoms() | self.operand.atoms()

    def free_variables(self):
        return self.operator.free_variables() | self.operand.free_variables()

    
class Abstraction(object):
    def __init__(self, bound, body):
        if not is_variable(bound):
            raise TypeError('bound terms must be variables')

        self._bound = bound
        self._body = body

    @property
    def bound(self):
        return self._bound

    @property
    def body(self):
        return self._body
        
    @property
    def qtype(self):
        return qtype.qfun(self.bound.qtype, self.body.qtype)
    
    def __repr__(self):
        return 'Abstraction(%r, %r)' % (self.bound, self.body)

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.bound == other.bound
                and self.body == other.body)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.__class__) ^ hash(self.bound) ^ hash(self.body)

    def atoms(self):
        return self.body.atoms() | set([self.bound])

    def free_variables(self):
        return self.body.free_variables() - set([self.bound])

