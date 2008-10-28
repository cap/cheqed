from qterm import is_variable, is_constant, is_combination, is_abstraction
from qtype_unifier import can_unify 

class TermMatcher:
    def __init__(self):
        self.assignments = {}

    def match_term(self, pattern, term):
        if is_variable(pattern):
            self.match_variable(pattern, term)
        elif is_constant(pattern) and is_constant(term):
            self.match_constant(pattern, term)
        elif is_combination(pattern) and is_combination(term):
            self.match_combination(pattern, term)
        elif is_abstraction(pattern) and is_abstraction(term):
            self.match_abstraction(pattern, term)
        else:
            self.fail(pattern, term)

    def match_variable(self, pattern, term):
        if can_unify([pattern.qtype, term.qtype]):
            if pattern.name in self.assignments:
                if self.assignments[pattern.name] == term:
                    return
                raise UnificationError('Cannot match %s with both %s and %s.'
                                       % (pattern, term,
                                          assignments[pattern.name]))
            self.assignments[pattern.name] = term
        else:
            self.fail(pattern, term)

    def match_constant(self, pattern, term):
        if pattern.name != term.name \
                or not can_unify([pattern.qtype, term.qtype]):
            self.fail(pattern, term)

    def match_combination(self, pattern, term):
        self.match_term(pattern.operator, term.operator)
        self.match_term(pattern.operand, term.operand)

    def match_abstraction(self, pattern, term):
        self.match_term(pattern.bound, term.bound)
        self.match_term(pattern.body, term.body)

def match_term(term, pattern):
    matcher = TermMatcher()
    matcher.match_term(term, pattern)
    return matcher.assignments
