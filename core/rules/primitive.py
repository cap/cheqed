from cheqed.core import qterm, unification
from cheqed.core.sequent import Sequent
from cheqed.core.rules.match import match_first, match_second
    
# helper functions
def permute(list_, index):
    return [list_[index]] + list_[:index] + list_[index + 1:]

def contract(list_):
    return [list_[0]] + list_

def weaken(list_):
    return list_[1:]

# structural rules
def left_permutation(sequent, index):
    return [Sequent(permute(sequent.left, index), sequent.right)]

def right_permutation(sequent, index):
    return [Sequent(sequent.left, permute(sequent.right, index))]

def left_contraction(sequent):
    return [Sequent(contract(sequent.left), sequent.right)]

def right_contraction(sequent):
    return [Sequent(sequent.left, contract(sequent.right))]

def left_weakening(sequent):
    return [Sequent(weaken(sequent.left), sequent.right)]

def right_weakening(sequent):
    return [Sequent(sequent.left, weaken(sequent.right))]

# logical rules
def axiom(sequent):
    if sequent.left[0] != sequent.right[0]:
        raise unification.UnificationError('axiom does not apply:'
                                           ' %s is not the same as %s'
                                           % (sequent.left[0],
                                              sequent.right[0]))
    return []

def cut(sequent, witness):
    return [Sequent(sequent.left, [witness] + sequent.right),
            Sequent([witness] + sequent.left, sequent.right)]

def left_negation(sequent):
    match = match_first(sequent, 'left', 'not a')
    return [Sequent(sequent.left[1:], [match['a']] + sequent.right)]

def right_negation(sequent):
    match = match_first(sequent, 'right', 'not a')
    return [Sequent([match['a']] + sequent.left, sequent.right[1:])]

def left_disjunction(sequent):
    match = match_first(sequent, 'left', 'a or b')
    return [Sequent([match['a']] + sequent.left[1:], sequent.right),
            Sequent([match['b']] + sequent.left[1:], sequent.right)]

def right_disjunction(sequent):
    match = match_first(sequent, 'right', 'a or b')
    return [Sequent(sequent.left,
                    [match['a'], match['b']] + sequent.right[1:])]

def left_universal(sequent, witness):
    match = match_first(sequent, 'left', 'for_all x . phi')
    return [Sequent([match['phi'].substitute(witness, match['x'])]
                    + sequent.left,
                    sequent.right)]

def right_universal(sequent, witness):
    match = match_first(sequent, 'right', 'for_all x . phi')

    if (not witness.is_variable
        or witness.name in [var.name for var in sequent.free_variables()]):
        raise unification.UnificationError('Cannot use %s as a witness in %s.'
                                           % (witness, sequent.right[0]))

    return [Sequent(sequent.left,
                    [match['phi'].substitute(witness, match['x'])]
                    + sequent.right[1:])]

def left_schema(sequent, witness):
    match = match_first(sequent, 'left', 'schema phi . psi')
    return [Sequent([match['psi'].substitute(witness, match['phi'], respect_bound=True)]
                    + sequent.left,
                    sequent.right)]

def left_substitution(sequent):
    match = match_second(sequent, 'left', 'a = b')

    return [Sequent(([sequent.left[0].substitute(match['b'], match['a'])]
                     + sequent.left[1:]),
                    sequent.right)]

def right_substitution(sequent):
    match = match_first(sequent, 'left', 'a = b')

    return [Sequent(sequent.left,
                    ([sequent.right[0].substitute(match['b'], match['a'])]
                     + sequent.right[1:]))]

def left_symmetry(sequent):
    match = match_first(sequent, 'left', 'a = b')
    equals = sequent.left[0].operator.operator
    return [Sequent([qterm.binary_op(equals, match['b'], match['a'])]
                    + sequent.left[1:],
                    sequent.right)]

def right_symmetry(sequent):
    match = match_first(sequent, 'right', 'a = b')
    equals = sequent.right[0].operator.operator
    return [Sequent(sequent.left,
                    [qterm.binary_op(equals, match['b'], match['a'])]
                    + sequent.right[1:])]
