'''Represent terms in the simply typed lambda calculus.

I've changed my mind many times on the role and structure of these
objects.

Coming from ML and inspired by HOL, it is tempting to make classes
very small and write methods which dispatch in the style of pattern
matching. This has the advantage of grouping code in a very logical
way: we're more likely to think of substitution on terms rather than
on a particular type of term. Further, we don't encounter the typical
problems with this visitor-like pattern; we won't be adding new
classes to the hierarchy.

That said, for a small subset of operations, structuring the classes
pythonically seems to make sense. Why write a new function to dispatch
on term type, especially for single dispatch, when we already have the
Python object system?

I think the clinching factor is that there are very few things that we
want to do which involve just the objects themselves. Substitution is
really a method for building a new term from an old one. The term
construction process contains more nuance than belongs in a simple
constructor, and so substitution cannot be written as an instance
method without introducing a truly nasty dependency graph.

'''

from cheqed.core import qtype

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
    if a.qtype != b.qtype:
        raise TypeError('cannot substitute term of type %s for term of type %s'
                        % (a.qtype, b.qtype))




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

    def substitute_type(self, a, b):
        return Constant(self.name, self.qtype.substitute(a, b))


class Variable(Atom):
    def __repr__(self):
        return 'Variable(%r, %r)' % (self.name, self.qtype)

    def free_variables(self):
        return set([self])

    def substitute_type(self, a, b):
        return Variable(self.name, self.qtype.substitute(a, b))


class Combination(object):
    def __init__(self, operator, operand):
        if not qtype.is_fun(operator.qtype):
            raise TypeError('operator qtype must be "fun"')

        if operator.qtype.args[0] != operand.qtype:
            raise TypeError('operand type must match operator argument type')
        
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

    def substitute_type(self, a, b):
        return Combination(self.operator.substitute_type(a, b),
                           self.operand.substitute_type(a, b))    


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

    def substitute_type(self, a, b):
        return Abstraction(self.bound.substitute_type(a, b),
                           self.body.substitute_type(a, b))
