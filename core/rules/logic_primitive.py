import qterm, unification

@primitive
@applicable(lambda goal: False)
def assumption(goal):
    return []

@primitive
@applicable(lambda goal: False)
def noop(goal):
    return [goal]

@primitive
@applicable(lambda goal: False)
def axiom(goal):
    if goal.left[0] != goal.right[0]:
        raise Exception('axiom does not apply: %s is not the same as %s'
                        % (goal.left[0], goal.right[0]))
    return []

@primitive
@arg_types('term')
def cut(goal, witness):
    return [sequent(goal.left, [witness] + goal.right),
            sequent([witness] + goal.left, goal.right)]

@primitive
def left_negation(goal):
    match_ = match(goal.left[0], 'not a')
    return [sequent(goal.left[1:], [match_['a']] + goal.right)]

@primitive
def right_negation(goal):
    match_ = match(goal.right[0], 'not a')
    return [sequent([match_['a']] + goal.left, goal.right[1:])]

@primitive
def left_disjunction(goal):
    match_ = match(goal.left[0], 'a or b')
    return [sequent([match_['a']] + goal.left[1:], goal.right),
            sequent([match_['b']] + goal.left[1:], goal.right)]

@primitive
def right_disjunction(goal):
    match_ = match(goal.right[0], 'a or b')
    return [sequent(goal.left,
                    [match_['a'], match_['b']] + goal.right[1:])]

@primitive
@arg_types('term')
@applicable(lambda goal: match(goal.left[0], 'for_all x . phi'))
def left_universal(goal, witness):
    match_ = match(goal.left[0], 'for_all x . phi')
    return [sequent([substitute(match_['phi'], witness, match_['x'])]
                    + goal.left,
                    goal.right)]

@primitive
@arg_types('term')
@applicable(lambda goal: match(goal.right[0], 'for_all x . phi'))
def right_universal(goal, witness):
    match_ = match(goal.right[0], 'for_all x . phi')

    if (not is_variable(witness)
        or witness.name in [var.name for var in goal.free_variables()]):
        raise unification.UnificationError('Cannot use %s as a witness in %s.'
                                           % (witness, goal.right[0]))

    return [sequent(goal.left,
                    [substitute(match_['phi'], witness, match_['x'])]
                    + goal.right[1:])]

@primitive
@arg_types('term')
@applicable(lambda goal: match(goal.left[0], 'schema phi . psi'))
def left_schema(goal, witness):
    match_ = match(goal.left[0], 'schema phi . psi')
    return [sequent([substitute(match_['psi'], witness, match_['phi'])]
                    + goal.left,
                    goal.right)]

@primitive
def left_substitution(goal):
    match_ = match(goal.left[1], 'a = b')
    return [sequent(([substitute(goal.left[0], match_['b'], match_['a'])]
                     + goal.left[1:]),
                    goal.right)]

@primitive
def right_substitution(goal):
    match_ = match(goal.left[0], 'a = b')
    return [sequent(goal.left,
                    ([substitute(goal.right[0], match_['b'], match_['a'])]
                     + goal.right[1:]))]

@primitive
def left_symmetry(goal):
    match_ = match(goal.left[0], 'a = b')
    equals = goal.left[0].operator.operator
    return [sequent([qterm.binary_op(equals, match_['b'], match_['a'])]
                    + goal.left[1:],
                    goal.right)]

@primitive
def right_symmetry(goal):
    match_ = match(goal.right[0], 'a = b')
    equals = goal.right[0].operator.operator
    return [sequent(goal.left,
                    [qterm.binary_op(equals, match_['b'], match_['a'])]
                    + goal.right[1:])]
