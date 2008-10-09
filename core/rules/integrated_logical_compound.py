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
