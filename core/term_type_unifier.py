from cheqed.core.qtype_unifier import TypeUnifier
from cheqed.core.qterm import by_name

class TermTypeUnifier:
    '''Unify the types of free variables.

    The resultant unifier ensures that all free variables with a given
    name have the same type.
    '''

    def __init__(self):
        self.unifier = TypeUnifier()

    def add_terms(self, terms):
        all_frees = set()
        for term_frees in (term.free_variables() for term in terms):
            all_frees.update(term_frees)

        for frees in by_name(all_frees).values():
            self.unifier.unify_many([free.qtype for free in frees])

    def apply(self, term):
        for key, value in self.get_substitutions().iteritems():
            term = term.substitute_type(value, key)
        return term

    def get_substitutions(self):
        return self.unifier.get_substitutions()

def unify_types(terms):
    unifier = TermTypeUnifier()
    unifier.add_terms(terms)
    return [unifier.apply(term) for term in terms]
