from cheqed.core.rules.registry import register, rule
from cheqed.core.rules import primitive

@register
def left_contraction():
    return rule(primitive.left_contraction, 'left_contraction()')

@register
def right_contraction():
    return rule(primitive.right_contraction, 'right_contraction()')

@register
def left_weakening():
    return rule(primitive.left_weakening, 'left_weakening()')

@register
def right_weakening():
    return rule(primitive.right_weakening, 'right_weakening()')

@register
def left_permutation(index):
    return rule(lambda x: primitive.left_permutation(x, index),
                'left_permutation(%d)' % index)

@register
def right_permutation(index):
    return rule(lambda x: primitive.right_permutation(x, index),
                'right_permutation(%d)' % index)
