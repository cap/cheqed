@compound
@arg_types('term')
@applicable(lambda goal: match(goal.right[0], 'a = b'))
def right_extension(goal, witness):
    match_ = match(goal.right[0], 'a = b')
    return sequence(theorem_cut('set.extensionality'),
                    left_universal(match_['a']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match_['b']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(witness),
                    left_permutation(1),
                    left_weakening(),
                    branch(left_implication(),
                           right_bidirectional(),
                           axiom()))

@compound
@arg_types('term')
@applicable(lambda goal: match(goal.left[0], 'a subset b'))
def left_subset(goal, witness):
    return sequence(left_expand('subset'),
                    left_universal(witness),
                    left_permutation(1),
                    left_weakening(),
                    left_implication())

@compound
@arg_types('term')
@applicable(lambda goal: match(goal.right[0], 'a subset b'))
def right_subset(goal, witness):
    return sequence(right_expand('subset'),
                    right_universal(witness),
                    right_implication())

@compound
def left_powerset(goal):
    match_ = match(goal.left[0], 'a in powerset(b)')
    return sequence(theorem_cut('set.powerset'),
                    left_universal(match_['b']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match_['a']),
                    left_permutation(1),
                    left_weakening(),
                    branch(left_bidirectional(),
                           axiom(),
                           left_weakening()))

@compound
def right_powerset(goal):
    match_ = match(goal.right[0], 'a in powerset(b)')
    return sequence(theorem_cut('set.powerset'),
                    left_universal(match_['b']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match_['a']),
                    left_permutation(1),
                    left_weakening(),
                    branch(left_bidirectional(),
                           right_weakening(),
                           axiom()))

@compound
@applicable(lambda goal: match(goal.right[0], 'x in separation(X, phi)'))
def right_separation(goal):
    match_ = match(goal.right[0], 'x in separation(X, phi)')
    return sequence(theorem_cut('set.separation'),
                    left_schema(match_['phi']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match_['X']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match_['x']),
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

@compound
@applicable(lambda goal: match(goal.left[0], 'x in separation(X, phi)'))
def left_separation(goal):
    match_ = match(goal.left[0], 'x in separation(X, phi)')
    return sequence(theorem_cut('set.separation'),
                    left_schema(match_['phi']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match_['X']),
                    left_permutation(1),
                    left_weakening(),
                    left_universal(match_['x']),
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
