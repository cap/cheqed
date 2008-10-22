from cheqed.core.unification import Unifier, UnificationError

class TypeUnifier:
    def __init__(self):
        self.unifier = Unifier(lambda x: x.is_variable,
                               lambda x, y: x in y.atoms)

    def add_types(self, types):
        variables = [qtype for qtype in types if qtype.is_variable]
        compounds = [qtype for qtype in types if not qtype.is_variable]
        self.add_variables(variables, compounds)
        self.add_compounds(compounds)

    def add_variables(self, variables, compounds):
        if len(variables) > 0:
            if len(compounds) > 0:
                representative = compounds[0]
            else:
                representative = variables[0]

            for variable in variables:
                if variable != representative:
                    self.unifier.add_subs(variable, representative)

    def add_compounds(self, compounds):
        if len(compounds) > 0:
            names = [comp.name for comp in compounds]
            for name in names:
                if name != names[0]:
                    raise UnificationError('Cannot unify %s with %s'
                                           % (name, names[0]))

            args = [comp.args for comp in compounds]
            for arg in args:
                if len(arg) != len(args[0]):
                    raise UnificationError('unfiymanytypes:len')

            for equiv in zip(*args):
                self.add_types(equiv)

    def get_substitutions(self):
        return self.unifier.get_substitutions()

    def unify(self, qtype):
        for key, value in self.get_substitutions().iteritems():
            qtype = qtype.substitute(value, key)
        return qtype

def unify(types):
    if len(types) == 0:
        return None
    
    unifier = TypeUnifier()
    unifier.add_types(types)
    return unifier.unify(types[0])

class QTypeError(Exception):
    def __init__(self, message=''):
        Exception.__init__(self, message)

class QTypeVariable(object):
    _index = 0
    
    def __init__(self):
        self._index = QTypeVariable._index
        QTypeVariable._index += 1

    def __contains__(self, other):
        if self == other:
            return True
        else:
            return False

    @property
    def atoms(self):
        return set([self])
        
    @property
    def is_variable(self):
        return True
        
    @property
    def name(self):
        return '?v%d' % self._index

    @property
    def args(self):
        return []

    def substitute(self, a, b):
        if self == b:
            return a
        else:
            return self

    def unify(self, other):
        return unify([other, self])

    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self._index == other._index)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self._index)
            
class QType(object):
    _arity = {
        'obj': 0,
        'bool': 0,
        'fun': 2,
        }

    def __init__(self, name, args):
        try:
            if self._arity[name] != len(args):
                raise QTypeError('QType "%s" requires %d arguments,'
                                 ' received %d.'
                                % (name, self._arity[name], len(args)))
        except KeyError:
            raise QTypeError('"%s" is not a declared qtype.' % name)

        self._name = name
        self._args = args

    @property
    def atoms(self):
        result = set()
        if len(self._args) == 0:
            result.add(self)
        for arg in self.args:
            result.update(arg.atoms)
        return result
        
    @property
    def is_variable(self):
        return False

    @property
    def name(self):
        return self._name

    @property
    def args(self):
        return self._args

    def substitute(self, a, b):
        args = [ arg.substitute(a, b) for arg in self.args ]
        if args != self.args:
            return QType(self.name, args)
        else:
            return self

    def unify(self, other):
        return unify([other, self])
    
    def __repr__(self):
        if self.name == 'fun':
            return '(%s->%s)' % (str(self.args[0]), str(self.args[1]))
        elif self.name in ['obj', 'bool']:
            return self.name
        else:
            return NotImplemented

    def __eq__(self, other):
        return (self.name == other.name
                and self.args == other.args)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        result = 0
        for arg in self.args:
            result = result ^ hash(arg)
        
        return result ^ hash(self.name)

def qobj():
    return QType('obj', [])

def qbool():
    return QType('bool', [])

def qfun(a, b):
    return QType('fun', [a, b])

def qvar():
    return QTypeVariable()
