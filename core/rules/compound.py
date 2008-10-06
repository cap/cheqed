from cheqed.core.rules.registry import register, make_compound, applicable
from cheqed.core.plan import assumption, branch, pair, sequence

from cheqed.core.rules.structural import *
from cheqed.core.rules.logical import *

@register
@make_compound
def qed(goal):
    for i, left in enumerate(goal.left):
        for j, right in enumerate(goal.right):
            if left == right:
                return sequence(left_permutation(i),
                                right_permutation(j),
                                axiom())
    raise Exception('qed does not apply.')

@register
@make_compound
def left_conjunction(goal):
    return sequence(left_expand('and'),
                    left_negation(),
                    right_disjunction(),
                    right_negation(),
                    right_negation(),
                    left_permutation(1))

@register
@make_compound
def right_conjunction(goal):
    return sequence(right_expand('and'),
                    right_negation(),
                    branch(left_disjunction(),
                          left_negation(),
                          left_negation()))

@register
@make_compound
def left_implication(goal):
    return sequence(left_expand('implies'),
                    branch(left_disjunction(),
                           left_negation(),
                           assumption()))

@register
@make_compound
def right_implication(goal):
    return sequence(right_expand('implies'),
                    right_disjunction(),
                    right_negation())

@register
@make_compound
def right_bidirectional(goal):
    return sequence(right_expand('iff'),
                    branch(right_conjunction(),
                           right_implication(),
                           right_implication()))

@register
@make_compound
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
                                           assumption()))))

@applicable('right', 'exists x . phi')
@register
@make_compound
def right_existential(goal, witness):
    return sequence(right_contraction(),
                    right_expand('exists'),
                    right_negation(),
                    left_universal(witness),
                    left_negation(),
                    left_weakening())

@applicable('left', 'exists x . phi')
@register
@make_compound
def left_existential(goal, witness):
    return sequence(left_expand('exists'),
                    left_negation(),
                    right_universal(witness),
                    right_negation())

@applicable('right', 'a = b')
@register
@make_compound
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

@applicable('left', 'a subset b')
@register
@make_compound
def left_subset(goal, witness):
    return sequence(left_expand('subset'),
                    left_universal(witness),
                    left_permutation(1),
                    left_weakening(),
                    left_implication())

@applicable('right', 'a subset b')
@register
@make_compound
def right_subset(goal, witness):
    return sequence(right_expand('subset'),
                    right_universal(witness),
                    right_implication())

@register
@make_compound
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

@register
@make_compound
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

@applicable('right', 'x in separation(X, phi)')
@register
@make_compound
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

@applicable('left', 'x in separation(X, phi)')
@register
@make_compound
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

