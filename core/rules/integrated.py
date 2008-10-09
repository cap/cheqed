@compound
def excluded_middle(goal):
    return sequence(
        right_disjunction(),
        right_permutation(1),
        right_negation(),
        axiom())

# @primitive
# @arg_types('term')
# def right_universal(witness, goal):
#     match = match_first(goal, 'right', 'for_all x . phi')
#     if (not witness.is_variable
#         or witness.name in [var.name for var in goal.free_variables()]):
#         raise unification.UnificationError('Cannot use %s as a witness in %s.'
#                                            % (witness, goal.right[0]))

#     return [Sequent(goal.left,
#                     [match['phi'].substitute(witness, match['x'])]
#                     + goal.right[1:])]

# @compound
# def left_conjunction(goal):
#     return [[left_expand, 'and'],
#             [left_negation,
#              [right_disjunction,
#               [right_negation,
#                [right_negation,
#                 [left_permutation, 1]]]]]]

'''
Forward reasoning: start with our axioms and inference rules, use them
to build more complex statements which must be true.

Backwards reasoning: start with a statement we believe to be true and
deconstruct it using inference rule inverses. If all statements can be
traced to axioms, our proof is complete and valid.

We want to focus on backwards reasoning. We need to define the tools
we'll use to do it.

At a very basic level, we have functions of type sequent->(sequent
list) which take a goal sequent, apply an inverse inference rule, and
return a list of subgoals we must prove in turn. We will call these FOOs.

To complete a proof, all we need are FOOs. We can build compound FOOs,
or FOOs whose behavior depends on the goal, or FOOs which represent an
entire proof. Problem solved.

This approach is problematic in that it doesn't match our way of
thinking very well. If we have a compound FOO or a FOO which finishes
an entire proof, we want to look inside it. If we have a FOO whose
behavior depends on the goal, we want to see which steps it actually
performed for a particular goal.

What we're looking for is some way of exposing the inner workings of a
FOO. Programming languages have debuggers, which allow us to step
through programs instruction by instruction. Since a proof in our
curren sense is just a program, why not use an existing debugger?
Existing debuggers operate with granularity appropriate to
programming, that is, at the level of function calls and
statements. This is not what we want; if an equation-solving FOO tries
many possible operations before finding one that works, we don't care
much about the search process. We only care about the result.

This said, we don't just want to expose the result wholesale. We'd
like to retain some of the FOOs structure. If our equation-solving FOO
settles on some sequence of calls to other FOOs, we would like to see
that it was our equation-solving FOO that resulted in these calls, not
simply that they occured.

So at some level all we need is a sequence of primitive FOOs which are
inverse inference rules. We want to know why we are using this
particular sequence, that is, we want to know which other, complex
FOOs generated the sequence. So we could write complex FOOs which act
like code generators, returning sequences of primitive FOOs. To retain
the structure of the process which generated the sequence, we could
annotate the final sequence: this primitive FOO resulted from this
complex FOO.

Unfortunately, we cannot completely separate the generation phase from
the evaluation phase. We want to write FOOs whose behavior depends on
the goal to which they are applied. At each step in the generation
phase, we need the result of the previous step.

We are stuck walking the graph of complex FOOs, generating proofs,
evaluating them, and moving to the next node. How do we represent this?

Our basic, visible structure for this is as follows. Let G be our
goal, let A...E be FOOs.

Apply A to G, resulting in G1.
Apply B to G1, resulting in G2 and G3.
Apply C to G2, solving this goal.
Apply D to G3 with argument 'x', resulting in G4.
Apply E to G4, solving this goal.
QED.

This is a sequence of instructions saying "Do X. On the
results of X, do Y and Z."

-------

Two kinds of rules: primitives and compounds. Both take a sequent
argument. Primitives return a list of sequents, compounds return a
list of rules.

What we store as a "proof" is actually a mixture of primitives,
compounds, and function calls which result in primitives or
compounds. Some functions take arguments, such as the term with which
to instantiate a quantified variable, which then return the actual
rule to do the instantiation.

Of course, we also need to be able to pretty-print these things, so the functions should all be able to print themselves back out... somehow... here's where the typing system could come in handy...
'''

# [left_negation,
#  [right_negation,
#   [right_conjunction,
#    [left_negation,
#     assumption],
#    [right_negation,
#     [left_universal(x),
#      qed]]]]]

# type primitive = sequent->sequent list

# type rule =
#   | Primitive of primitive
#   | Compound of sequent->rule tree

# left_negation:sequent->sequent list
# left_universal:term->sequent->rule tree

# [left_negation,
#  [right_negation,
#   [right_conjunction,
#    [left_negation,
#     [assumption]],
#    [right_negation,
#     [[left_universal, 'x'],
#      [qed]]]]]]

# (left_negation
#  (right_negation
#   (right_conjunction
#    (left_negation
#     (assumption))
#    (right_negation
#     (left_universal x)
#     (qed)))))
