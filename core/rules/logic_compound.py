@compound
def qed(goal):
    for i, left in enumerate(goal.left):
        for j, right in enumerate(goal.right):
            if left == right:
                return sequence(left_permutation(i),
                                right_permutation(j),
                                axiom())
    raise Exception('qed does not apply.')

@compound
def left_conjunction(goal):
    return sequence(left_expand('and'),
                    left_negation(),
                    right_disjunction(),
                    right_negation(),
                    right_negation(),
                    left_permutation(1))

@compound
def right_conjunction(goal):
    return sequence(right_expand('and'),
                    right_negation(),
                    branch(left_disjunction(),
                          left_negation(),
                          left_negation()))

@compound
def left_implication(goal):
    return sequence(left_expand('implies'),
                    branch(left_disjunction(),
                           left_negation(),
                           noop()))

@compound
def right_implication(goal):
    return sequence(right_expand('implies'),
                    right_disjunction(),
                    right_negation())

@compound
def right_bidirectional(goal):
    return sequence(right_expand('iff'),
                    branch(right_conjunction(),
                           right_implication(),
                           right_implication()))

@compound
def left_bidirectional(goal):
    return sequence(left_expand('iff'),
                    left_conjunction(),
                    branch(left_implication(),
                           branch(left_implication(),
                                  right_permutation(1),
                                  axiom()),
                           sequence(left_permutation(1),
                                    branch(left_implication(),
                                           axiom(),
                                           noop()))))

@compound
@arg_types('term')
@applicable(lambda goal: match(goal.right[0], 'exists x . phi'))
def right_existential(goal, witness):
    return sequence(right_contraction(),
                    right_expand('exists'),
                    right_negation(),
                    left_universal(witness),
                    left_negation(),
                    left_weakening())

@compound
@arg_types('term')
@applicable(lambda goal: match(goal.left[0], 'exists x . phi'))
def left_existential(goal, witness):
    return sequence(left_expand('exists'),
                    left_negation(),
                    right_universal(witness),
                    right_negation())
