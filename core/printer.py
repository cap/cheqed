from cheqed.core import qtype, qterm, unification

class Printer(object):
    def __init__(self, syntax):
        self.syntax = syntax

    def termlist(self, termlist):
        return ', '.join([self.term(term) for term in termlist])
        
    def sequent(self, sequent):
        return '%s |- %s' % (self.termlist(sequent.left),
                             self.termlist(sequent.right))

    def term(self, term):
        if term.is_constant or term.is_variable:
            return term.name
        if term.is_abstraction:
            return '(\\%s.%s)' % (self.term(term.bound),
                                  self.term(term.body))
        if term.is_combination:
            for operator in self.syntax.operators():
                op = operator.constant

                if operator.arity == 1:
                    pattern = qterm.unary_op(operator.constant,
                                             qterm.Variable('a',
                                                            qtype.qvar()))
                    
                    try:
                        match = qterm.match(pattern, term)
                    except unification.UnificationError:
                        continue
                    return '(%s %s)' % (op.name, self.term(match['a']))
                elif operator.arity == 2:
                    pattern = qterm.binary_op(operator.constant,
                                              qterm.Variable('a', qtype.qvar()),
                                              qterm.Variable('b', qtype.qvar()))
                    try:
                        match = qterm.match(pattern, term)
                    except unification.UnificationError:
                        continue
                    return '(%s %s %s)' % (self.term(match['a']),
                                         op.name,
                                         self.term(match['b']))
            for binder in self.syntax.binders():
                pattern = qterm.binder(binder.constant,
                                       qterm.Variable('a', qtype.qvar()),
                                       qterm.Variable('b', qtype.qvar()))
                try:
                    match = qterm.match(pattern, term)
                except unification.UnificationError:
                    continue
                return '(%s %s . %s)' % (binder.name,
                                       self.term(match['a']),
                                       self.term(match['b']))

            def uncurry(term):
                if not term.is_combination:
                    return term, []
                operator, operands = uncurry(term.operator)
                return operator, operands + [term.operand]

            operator, operands = uncurry(term)
            return '%s(%s)' % (self.term(operator),
                               ', '.join([self.term(rand) for rand in operands]))
