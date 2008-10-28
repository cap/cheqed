from cheqed.core import qtype, qtype_unifier, qterm
from cheqed.core.term_type_unifier import unify_types

def unary_op(op, a):
    return build_combination(op, a)

def binary_op(op, a, b):
    return build_combination(build_combination(op, a), b)

def binder(op, x, a):
    return unary_op(op, build_abstraction(x, a))

def build_variable(name, qtype_):
    return qterm.Variable(name, qtype_)

def build_constant(name, qtype_):
    return qterm.Constant(name, qtype_)

def build_combination(operator, operand):
    if qtype.is_variable(operator.qtype):
        operator = qterm.substitute_type(operator,
                                         qtype.qfun(operand.qtype,
                                                    qtype.qvar()),
                                         operator.qtype)

    if operator.qtype.name != 'fun':
        raise TypeError('operators must be functions')

    unifier = qtype_unifier.TypeUnifier()
    unifier.unify(operator.qtype.args[0], operand.qtype)
    for key, value in unifier.get_substitutions().iteritems():
        operator = qterm.substitute_type(operator, value, key)
        operand = qterm.substitute_type(operand, value, key)

    operator, operand = unify_types([operator, operand])

    if operator.qtype.args[0] != operand.qtype:
        raise TypeError('operand type must match operator argument type')

    return qterm.Combination(operator, operand)

def build_abstraction(bound, body):
    bound, body = unify_types([bound, body])
    return qterm.Abstraction(bound, body)
