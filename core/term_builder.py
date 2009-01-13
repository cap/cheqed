from cheqed.core import qtype, qtype_unifier, qterm
from cheqed.core.term_type_unifier import unify_types

class DumbTermBuilder:
    def build_constant(self, name, type_):
        return qterm.Constant(name, type_)

    def build_variable(self, name, type_):
        return qterm.Variable(name, type_)

    def build_combination(self, operator, operand):
        return qterm.Combination(operator, operand)

    def build_abstraction(self, bound, body):
        return qterm.Abstraction(bound, body)

class TypeInferringTermBuilder:
    def build_constant(self, name, type_):
        return qterm.Constant(name, type_)

    def build_variable(self, name, type_):
        return qterm.Variable(name, type_)

    def build_combination(self, operator, operand):
        if qtype.is_variable(operator.qtype):
            operator = operator.substitute_type(qtype.qfun(operand.qtype,
                                                           qtype.qvar()),
                                                operator.qtype)

        if operator.qtype.name != 'fun':
            raise TypeError('operators must be functions')

        unifier = qtype_unifier.TypeUnifier()
        unifier.unify(operator.qtype.args[0], operand.qtype)
        for key, value in unifier.get_substitutions().iteritems():
            operator = operator.substitute_type(value, key)
            operand = operand.substitute_type(value, key)

        operator, operand = unify_types([operator, operand])

        if operator.qtype.args[0] != operand.qtype:
            raise TypeError('operand type must match operator argument type')

        return qterm.Combination(operator, operand)

    def build_abstraction(self, bound, body):
        bound, body = unify_types([bound, body])
        return qterm.Abstraction(bound, body)

class CompoundTermBuilder:
    def __init__(self, base_term_builder):
        self.base = base_term_builder

    def build_constant(self, name, type_):
        return self.base.build_constant(name, type_)

    def build_variable(self, name, type_):
        return self.base.build_variable(name, type_)

    def build_combination(self, operator, operand):
        return self.base.build_combination(operator, operand)

    def build_abstraction(self, bound, body):
        return self.base.build_abstraction(bound, body)

    def build_binary_op(self, operator, operand_0, operand_1):
        return self.base.build_combination(
            self.build_combination(operator, operand_0), operand_1)

    def build_binder(self, binder, bound, body):
        return self.base.build_combination(
            binder, self.base.build_abstraction(bound, body))

builder = CompoundTermBuilder(TypeInferringTermBuilder())    

build_variable = builder.build_variable
build_constant = builder.build_constant
build_combination = builder.build_combination
build_abstraction = builder.build_abstraction

build_binary_op = builder.build_binary_op
build_binder = builder.build_binder
