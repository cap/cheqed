from cheqed.core import qterm
from cheqed.core.term_builder import TypeInferringTermBuilder

def beta_reduce(term):
    if not qterm.is_combination(term):
        return term
    
    if qterm.is_abstraction(term.operator):
        return substitute(term.operand, term.operator.bound, term.operator.body)
    return term


class Substitution:
    def __init__(self, value, pattern, term_builder=TypeInferringTermBuilder()):
        self.value = value
        self.pattern = pattern
        self.term_builder = term_builder

    def apply_to_atom(self, atom):
        if atom == self.pattern:
            return self.value
        else:
            return atom

    def apply_to_combination(self, combination):
        operator = self.apply_to_term(combination.operator)
        operand = self.apply_to_term(combination.operand)
        combination = self.term_builder.build_combination(operator, operand)
        return beta_reduce(combination)

    def apply_to_abstraction(self, abstraction):
        if abstraction.bound in self.pattern.free_variables():
            return abstraction

        bound = abstraction.bound
        body = abstraction.body
        a_names = set([var.name for var in self.value.free_variables()])
        if bound.name in a_names:
            names = set([var.name for var in body.atoms()]) \
                | a_names
            new_name = bound.name
            i = 1
            while new_name in names:
                new_name = bound.name + str(i)
                i += 1
            new_bound = self.term_builder.build_variable(new_name, bound.qtype)
            body = substitute(new_bound, bound, body)
            bound = new_bound
        body = substitute(self.value, self.pattern, body)
        return self.term_builder.build_abstraction(bound, body)

    def apply_to_term(self, term):
        if qterm.is_atom(term):
            return self.apply_to_atom(term)
        elif qterm.is_combination(term):
            return self.apply_to_combination(term)
        elif qterm.is_abstraction(term):
            return self.apply_to_abstraction(term)
        else:
            raise Exception('unrecognized term')

def substitute(value, pattern, term):
    return Substitution(value, pattern).apply_to_term(term)
