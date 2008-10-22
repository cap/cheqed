class UnificationError(Exception):
    pass

class Unifier:
    def __init__(self, is_variable, occurs_in):
        self.is_variable = is_variable
        self.occurs_in = occurs_in
        self.subs = []
        
    def add_subs(self, a, b):
        self.subs.append((a, b))

    def fail(self, a, b):
        raise UnificationError('Cannot unify %s with %s.' % (a, b))
        
    def occurs_check(self, a, b):
        if self.occurs_in(a, b):
            self.fail(a, b)
        
    def get_substitutions(self):
        r = {}
        for a, b in self.subs:
            if a in r:
                self.subs.append((b, r[a]))
                self.occurs_check(a, b)
                r[a] = b
            elif b in r:
                self.subs.append((a, r[b]))
                self.occurs_check(b, a)
                r[b] = a
            elif a != b:
                if not self.is_variable(a):
                    a, b = b, a
                if not self.is_variable(a):
                    self.fail(a, b)

                for c in r:
                    if r[c] == a:
                        self.occurs_check(c, b)
                        r[c] = b
                r[a] = b
                self.occurs_check(a, b)
        return r
