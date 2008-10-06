from cheqed.core.rules.registry import register, applicable, rule
from cheqed.core.rules import primitive

@register
def axiom():
    return rule(primitive.axiom, 'axiom()')

@register
def cut(witness):
    return rule(lambda x: primitive.cut(x, witness),
                lambda printer: "cut(parse(r'%s'))" \
                    % printer.term(witness))

@register
def left_negation():
    return rule(primitive.left_negation, 'left_negation()')

@register
def right_negation():
    return rule(primitive.right_negation, 'right_negation()')

@register
def left_disjunction():
    return rule(primitive.left_disjunction, 'left_disjunction()')

@register
def right_disjunction():
    return rule(primitive.right_disjunction, 'right_disjunction()')

@register
@applicable('left', 'for_all x . phi')
def left_universal(witness):
    return rule(lambda x: primitive.left_universal(x, witness),
                lambda printer: "left_universal(parse(r'%s'))" % printer.term(witness))

@register
@applicable('right', 'for_all x . phi')
def right_universal(witness):
    return rule(lambda x: primitive.right_universal(x, witness),
                lambda printer: "right_universal(parse(r'%s'))" % printer.term(witness))

@register
@applicable('left', 'schema phi . psi')
def left_schema(witness):
    return rule(lambda x: primitive.left_schema(x, witness),
                lambda printer: "left_schema(parse(r'%s'))" % printer.term(witness))

@register
def left_substitution():
    return rule(primitive.left_substitution, 'left_substitution()')

@register
def right_substitution():
    return rule(primitive.right_substitution, 'right_substitution()')
