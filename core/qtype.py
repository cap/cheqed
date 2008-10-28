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


def is_atom(qtype):
    return isinstance(qtype, Atom)

def is_variable(qtype):
    return isinstance(qtype, Variable)

def is_constant(qtype):
    return isinstance(qtype, Constant)

def is_polymorphic(qtype):
    return isinstance(qtype, Polymorphic)

def is_fun(qtype):
    return qtype.name == 'fun'
