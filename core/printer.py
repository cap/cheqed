from cheqed.core import qtype, qterm, unification

def match_unary_op(term):
    return (term.operator,
            term.operand)

def match_binary_op(term):
    return (term.operator.operator,
            term.operator.operand,
            term.operand)

def match_binder(term):
    return (term.operator,
            term.operand.bound,
            term.operand.body)

class Printer(object):
    def __init__(self, syntax):
        self.syntax = syntax

    def term(self, term_):
        print term_
        return self.print_term(term_)

    def print_separation(term):
        bound, predicate = match_separation(term)
    
    def print_term(self, term):
        if term.is_constant or term.is_variable:
            return self.print_atom(term)
        if term.is_abstraction:
            return self.print_abstraction(term)
        if term.is_combination:
            return self.print_combination(term)

    def print_atom(self, atom):
        return atom.name

    def print_abstraction(self, abstraction):
        return '(\\%s. %s)' % (self.print_atom(abstraction.bound),
                               self.print_term(abstraction.body))

    def print_unary_operator(self, combination):
        operator, operand = match_unary_op(combination)
        for operator_ in self.syntax.operators():
            if operator_.arity == 1 and operator_.name == operator.name:
                return '(%s %s)' % (self.print_atom(operator),
                                    self.print_term(operand))
        raise TypeError

    def print_binary_operator(self, combination):
        operator, first, second = match_binary_op(combination)
        for operator_ in self.syntax.operators():
            if operator_.arity == 2 and operator_.name == operator.name:
                return '(%s %s %s)' % (self.print_term(first),
                                       self.print_atom(operator),
                                       self.print_term(second))
        raise TypeError

    def print_binder(self, combination):
        binder, bound, body = match_binder(combination)
        for binder_ in self.syntax.binders():
            if binder_.name == binder.name:
                return '(%s %s . %s)' % (self.print_atom(binder),
                                         self.print_atom(bound),
                                         self.print_term(body))
        raise TypeError
    
    def print_function(self, combination):
        def uncurry(term):
            if not term.is_combination:
                return term, []
            operator, operands = uncurry(term.operator)
            return operator, operands + [term.operand]

        operator, operands = uncurry(combination)
        
        pretty_args = ', '.join([self.print_term(o) for o in operands])
        return '%s(%s)' % (self.print_term(operator),
                           pretty_args)

    def print_combination(self, combination):
        for method in [self.print_unary_operator,
                       self.print_binary_operator,
                       self.print_binder,
                       self.print_function]:
            try:
                return method(combination)
            except (AttributeError, TypeError):
                pass

        raise TypeError
