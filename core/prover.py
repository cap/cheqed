import inspect

from cheqed.core import environment
from cheqed.core.sequent import Sequent
from cheqed.core.plan import Assumption, Compound, Rule, Branch
from cheqed.core.rules.match import match_first

from cheqed.core.rules import registry
from cheqed.core.rules.registry import register, make_compound, applicable

# import rule sets to register them
from cheqed.core.rules.structural import *
from cheqed.core.rules.logical import *

env = environment.load_modules('logic', 'set')
parse = env.parser.parse

def prettyprint(term):
    return env.printer.term(term)

def assumption():
    return Assumption()

def branch(first, *branches):
    return Branch(first, *branches)

def pair(first, second):
    return branch(first, second)

def sequence(*seq):
    if len(seq) == 0:
        raise 'sequence error: nothing to do.'
    if len(seq) == 1:
        return seq[0]
    return pair(seq[0], sequence(*seq[1:]))

# Definition expansion
def expand_definition(term, definition):
    atom, value = definition.operator.operand, definition.operand
    return term.substitute(value, atom)                    

def _left_expand(sequent, definition):
    return [Sequent(([expand_definition(sequent.left[0], definition)]
                     + sequent.left[1:]),
                    sequent.right)]

def _right_expand(sequent, definition):
    return [Sequent(sequent.left,
                    ([expand_definition(sequent.right[0], definition)]
                     + sequent.right[1:]))]

@register
def left_expand(name):
    return rule(lambda x: _left_expand(x, env.definitions[name]),
                'left_expand(%r)' % name)

@register
def right_expand(name):
    return rule(lambda x: _right_expand(x, env.definitions[name]),
                'right_expand(%r)' % name)

def _theorem(sequent):
    term = sequent.right[0]
    for thm in env.axioms.itervalues():
        if thm == term:
            return []
    raise unification.UnificationError('theorem does not apply.')

@register
def theorem():
    return rule(_theorem, 'theorem()')

@register
@make_compound
def theorem_cut(goal, name):
    return branch(cut(env.axioms[name]),
                  theorem(),
                  assumption())

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
def qed(goal):
    for i, left in enumerate(goal.left):
        for j, right in enumerate(goal.right):
            if left == right:
                return sequence(left_permutation(i),
                                right_permutation(j),
                                axiom())
    raise Exception('qed does not apply.')

propositional_rules = [
    (left_negation, 1),
    (right_negation, 1),
    (left_disjunction, 2),
    (right_disjunction, 1),
    (left_conjunction, 1),
    (right_conjunction, 2),
    (left_implication, 2),
    (right_implication, 1),
    (left_bidirectional, 2),
    (right_bidirectional, 2),
    ]

@register
@make_compound
def solve_propositional(goal):
    plan = assumption()
    applicable = []
    for rule, cost in propositional_rules:
        if is_applicable(rule, plan, goal):
            applicable.append((cost, rule))
    applicable.sort()

    if len(applicable) > 0:
        return applicable[0][1]()

    raise Exception('no applicable propositional rule')

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

def evaluate(string):
    return eval(string)

def is_applicable(func, goal):
    if hasattr(func, 'is_applicable'):
        return func.is_applicable(goal)

    if len(func.arg_names) > 0:
        return True

    try:
        tester = func()
        tester.subgoals(goal)
    except Exception, e:
        return False

    return True

def applicable_rules(prover, goal):
    subgoals = prover.subgoals(goal)
    if len(subgoals) == 0:
        return []

    applicable = []
    for func in registry.rules:
        if is_applicable(func, subgoals[0]):
            applicable.append((func.func_name, func.arg_names))

    return applicable
