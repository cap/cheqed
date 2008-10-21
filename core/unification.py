class UnificationError(Exception):
    pass

def unify(subs, is_variable, occurs_in):
    def occurs_check(a, b):
        if occurs_in(a, b):
            raise UnificationError('Cannot unify %s with %s.' % (a, b))
    r = {}
    for a, b in subs:
        if a in r:
            subs.append((b, r[a]))
            occurs_check(a, b)
            r[a] = b
        elif b in r:
            subs.append((a, r[b]))
            occurs_check(b, a)
            r[b] = a
        elif a != b:
            if not is_variable(a):
                a, b = b, a
            if not is_variable(a):
                raise UnificationError('Cannot unify %s with %s.' % (a, b))

            for c in r:
                if r[c] == a:
                    occurs_check(c, b)
                    r[c] = b
            r[a] = b
            occurs_check(a, b)
    return r

class Unifier:
    def __init__(self):
        self.subs = []

    def __repr__(self):
        return 'Unifier(%s)' % repr(self.subs)
        
    def add_subs(self, a, b):
        self.subs.append((a, b))

    def unified_subs(self,
                     is_variable=lambda x: x.is_variable,
                     atoms=lambda x: x.atoms):
        unifier = unify(self.subs, is_variable,
                        lambda x, y: x in atoms(y))
        return unifier
    
    def apply(self, other):
        subs = self.unified_subs()
        for key, value in subs.iteritems():
            other = other.substitute(value, key)
        return other
