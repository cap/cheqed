from cheqed.core.unification import Unifier, UnificationError

class QTypeError(Exception):
    def __init__(self, message=''):
        Exception.__init__(self, message)

def make_unifier(types, unifier=None):
    if unifier is None:
        unifier = Unifier()

    type_vars = [qtype for qtype in types if qtype.is_variable]
    type_comps = [qtype for qtype in types if not qtype.is_variable]

    # pick a representative with which to unify all variables
    if len(type_vars) > 0:
        rep = None
        if len(type_comps) > 0:
            rep = type_comps[0]
        else:
            rep = type_vars[0]

        for var in type_vars:
            if var != rep:
                unifier.add_subs(var, rep)

    # unify types (which may themselves contain type variables)
    if len(type_comps) > 0:
        names = [comp.name for comp in type_comps]
        for name in names:
            if name != names[0]:
                raise UnificationError('Cannot unify %s with %s'
                                       % (name, names[0]))

        args = [comp.args for comp in type_comps]
        for arg in args:
            if len(arg) != len(args[0]):
                raise UnificationError('unfiymanytypes:len')

        for equiv in zip(*args):
            unifier = make_unifier(equiv, unifier)

    return unifier

def unify(types):
    if len(types) == 0:
        return None
    
    unifier = make_unifier(types)
    rep = types[0]
    for key, value in unifier.unified_subs().iteritems():
        rep = rep.substitute(value, key)

    return rep

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
    def variables(self):
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
        'int': 0,
        'sequent': 0,
        'unit': 0,
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
    def variables(self):
        result = set()
        for arg in self.args:
            result.update(arg.variables)
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
        elif self.name in ['obj', 'bool', 'int', 'unit', 'sequent']:
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

def qclass():
    return QType('class', [])

def qobj():
    return QType('obj', [])

def qbool():
    return QType('bool', [])

def qunit():
    return QType('unit', [])

def qint():
    return QType('int', [])

def qsequent():
    return QType('sequent', [])

def qfun(a, b):
    return QType('fun', [a, b])

def qvar():
    return QTypeVariable()
