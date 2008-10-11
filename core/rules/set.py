#@applicable('right', 'a = b')
@compound
@arg_types('term')
def right_extension(goal, witness):
    match = match_first(goal, 'right', 'a = b')
    return sequence(theorem_cut('set.extensionality'),
                    left_universal(match['a']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match['b']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(witness),
                    left_permutation(1),
                    left_weakening(),
                    branch(left_implication(),
                           right_bidirectional(),
                           axiom()))

#@applicable('left', 'a subset b')
@compound
@arg_types('term')
def left_subset(goal, witness):
    return sequence(left_expand('subset'),
                    left_universal(witness),
                    left_permutation(1),
                    left_weakening(),
                    left_implication())

#@applicable('right', 'a subset b')
@compound
@arg_types('term')
def right_subset(goal, witness):
    return sequence(right_expand('subset'),
                    right_universal(witness),
                    right_implication())

@compound
def left_powerset(goal):
    match = match_first(goal, 'left', 'a in powerset(b)')
    return sequence(theorem_cut('set.powerset'),
                    left_universal(match['b']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match['a']),
                    left_permutation(1),
                    left_weakening(),
                    branch(left_bidirectional(),
                           axiom(),
                           left_weakening()))

@compound
def right_powerset(goal):
    match = match_first(goal, 'right', 'a in powerset(b)')
    return sequence(theorem_cut('set.powerset'),
                    left_universal(match['b']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match['a']),
                    left_permutation(1),
                    left_weakening(),
                    branch(left_bidirectional(),
                           right_weakening(),
                           axiom()))

#@applicable('right', 'x in separation(X, phi)')
@compound
def right_separation(goal):
    match = match_first(goal, 'right', 'x in separation(X, phi)')
    return sequence(theorem_cut('set.separation'),
                    left_schema(match['phi']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match['X']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match['x']),
                    left_permutation(1),
                    left_weakening(),
                    branch(left_bidirectional(),
                           sequence(right_weakening(),
                                    right_permutation(1),
                                    right_weakening(),
                                    right_negation(),
                                    branch(left_disjunction(),
                                           left_negation(),
                                           left_negation())),
                           axiom()))

#@applicable('left', 'x in separation(X, phi)')
@compound
def left_separation(goal):
    match = match_first(goal, 'left', 'x in separation(X, phi)')
    return sequence(theorem_cut('set.separation'),
                    left_schema(match['phi']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match['X']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match['x']),
                    left_permutation(1),
                    left_weakening(),
                    branch(left_bidirectional(),
                           axiom(),
                           sequence(left_weakening(),
                                    left_permutation(1),
                                    left_weakening(),
                                    left_negation(),
                                    right_disjunction(),
                                    right_negation(),
                                    right_negation(),
                                    left_permutation(1))))
