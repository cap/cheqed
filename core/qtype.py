from cheqed.core.unification import Unifier, UnificationError

class TypeUnifier:
    def __init__(self):
        self.unifier = Unifier(is_variable, lambda x, y: x in y.atoms())

    def unify_many(self, types):
        rep = types[0]
        for i in range(0, len(types)):
            self.unify(types[i], rep)

    def unify(self, a, b):
        if is_polymorphic(a) and is_polymorphic(b) and a.name == b.name:
            for arg_a, arg_b in zip(a.args, b.args):
                self.unify(arg_a, arg_b)
        else:
            self.unifier.unify(a, b)

    def get_substitutions(self):
        return self.unifier.get_substitutions()

    def apply(self, qtype):
        for key, value in self.get_substitutions().iteritems():
            qtype = qtype.substitute(value, key)
        return qtype

def unify(types):
    if len(types) == 0:
        return None
    
    unifier = TypeUnifier()
    unifier.unify_many(types)
    return unifier.apply(types[0])

def is_variable(qtype):
    return isinstance(qtype, Variable)

def is_constant(qtype):
    return isinstance(qtype, Constant)

def is_polymorphic(qtype):
    return isinstance(qtype, Polymorphic)

class Atom(object):
    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.name == other.name)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.__class__) ^ hash(self.name)

    @property
    def name(self):
        return self._name
    
    def atoms(self):
        return set([self])

class Variable(Atom):
    def substitute(self, a, b):
        if self == b:
            return a
        else:
            return self

class Constant(Atom):
    def substitute(self, a, b):
        return self

class Polymorphic(object):
    def __init__(self, name, args):
        self._name = name
        self._args = tuple(args)

    def __repr__(self):
        if self.name == 'fun':
            return '(%s->%s)' % (str(self.args[0]), str(self.args[1]))
        else:
            return NotImplemented

    def __eq__(self, other):
        return (self.name == other.name
                and self.args == other.args)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.__class__) ^ hash(self.name) ^ hash(self.args)

    @property
    def name(self):
        return self._name

    @property
    def args(self):
        return self._args

    def atoms(self):
        result = set()
        for arg in self.args:
            result.update(arg.atoms())
        return result
    
    def substitute(self, a, b):
        args = [ arg.substitute(a, b) for arg in self.args ]
        if args != self.args:
            return Polymorphic(self.name, args)
        else:
            return self

        
def qobj():
    return Constant('obj')

def qbool():
    return Constant('bool')

def qfun(a, b):
    return Polymorphic('fun', [a, b])

_variable_index = 0
def qvar():
    global _variable_index
    index = _variable_index
    _variable_index += 1
    return Variable('?v%d' % index)
