from cheqed.core.unification import Unifier
from cheqed.core.qtype import is_variable, is_polymorphic

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
