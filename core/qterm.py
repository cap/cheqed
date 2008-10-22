from cheqed.core.unification import Unifier, UnificationError
from cheqed.core import qtype, unification

def is_constant(term):
    return isinstance(term, Constant)

def is_variable(term):
    return isinstance(term, Variable)

def is_combination(term):
    return isinstance(term, Combination)

def is_abstraction(term):
    return isinstance(term, Abstraction)

def is_atom(term):
    return is_constant(term) or is_variable(term)

def is_term(term):
    return is_atom(term) or is_combination(term) or is_abstraction(term)

def free_variables(term):
    if is_constant(term):
        return set()
    elif is_variable(term):
        return set([term])
    elif is_combination(term):
        return free_variables(term.operator) | free_variables(term.operand)
    elif is_abstraction(term):
        return free_variables(term.body) - set([term.bound])

def atoms(term):
    if is_atom(term):
        return set([term])
    elif is_combination(term):
        return atoms(term.operator) | atoms(term.operand)
    elif is_abstraction(term):
        return atoms(term.body) | set([term.bound])

def replace(term, a, b):
    if is_atom(term):
        if term == b:
            return a
        else:
            return term
    elif is_combination(term):
        return Combination(replace(term.operator, a, b),
                           replace(term.operand, a, b)).beta_reduce()
    elif is_abstraction(term):
        return Abstraction(replace(term.bound, a, b),
                           replace(term.body, a, b))

def substitute(term, a, b):
    if is_atom(term):
        if term == b:
            return a
        else:
            return term
    elif is_combination(term):
        return Combination(substitute(term.operator, a, b),
                           substitute(term.operand, a, b)).beta_reduce()
    elif is_abstraction(term):
        if term.bound in free_variables(b):
            return term
        bound = term.bound
        body = term.body
        a_names = set([var.name for var in free_variables(a)])
        if bound.name in a_names:
            names = set([var.name for var in atoms(body)]) \
                | a_names
            new_name = bound.name
            i = 1
            while new_name in names:
                new_name = bound.name + str(i)
                i += 1
            new_bound = Variable(new_name, bound.qtype)
            body = substitute(body, new_bound, bound)
            bound = new_bound
        return Abstraction(bound, substitute(body, a, b))

def substitute_type(term, a, b):
    if is_constant(term):
        qtype = term.qtype.substitute(a, b)
        return Constant(term.name, qtype)
    elif is_variable(term):
        qtype = term.qtype.substitute(a, b)
        return Variable(term.name, qtype)
    elif is_combination(term):
        return Combination(substitute_type(term.operator, a, b),
                           substitute_type(term.operand, a, b))    
    elif is_abstraction(term):
        return Abstraction(substitute_type(term.bound, a, b),
                           substitute_type(term.body, a, b))

class TermUnifier:
    def __init__(self):
        self.unifier = Unifier(is_variable, lambda x, y: x in atoms(y))

    def fail(self, term, other):
        raise UnificationError('Cannot unify %s with %s.' % (term, other))
        
    def add_atom_subs(self, atom, other):
        if is_atom(other):
            if atom.name == other.name or atom.name == '=':
                return

        if is_variable(atom):
            try:
                qtype.unify([atom.qtype, other.qtype])
            except UnificationError, ue:
                self.fail(atom, other)

    #        atom.qtype.unify(other.qtype)
            self.unifier.add_subs(atom, other)
            return

        self.fail(atom, other)

    def add_term_subs(self, term, other):
        if is_constant(term) or is_variable(term):
            self.add_atom_subs(term, other)
        elif is_constant(other) or is_variable(other):
            self.add_atom_subs(other, term)
        elif is_combination(term) and is_combination(other):
            self.add_term_subs(term.operator, other.operator)
            self.add_term_subs(term.operand, other.operand)
        elif is_abstraction(term) and is_abstraction(other):
            self.add_term_subs(term.bound, other.bound)
            self.add_term_subs(term.body, other.body)
        else:
            self.fail(term, other)

    def get_substitutions(self):
        return self.unifier.get_substitutions()

    def unify(self, term, other):
        for key, value in self.get_substitutions().iteritems():
            term = replace(term, value, key)
            other = replace(other, value, key)

        term, other = unify_types([term, other])

        if term != other:
            self.fail(term, other)

        return term

def unify(term, other):
    unifier = TermUnifier()
    unifier.add_term_subs(term, other)
    return unifier.unify(term, other)

from cheqed.core.unification import UnificationError

def types_unify(types):
    try:
        qtype.unify(types)
        return True
    except UnificationError:
        return False

class TermTypeUnifier:
    def __init__(self):
        self.unifier = qtype.TypeUnifier()

    def add_terms(self, terms):
        atoms_by_name = {}
        for term in terms:
            for atom in free_variables(term):
                if atom.name != '=':
                    atoms_by_name.setdefault(atom.name, []).append(atom)

        for name, atoms in atoms_by_name.iteritems():
            if len(atoms) > 1:
                try:
                    self.unifier.add_types([atom.qtype for atom in atoms])
                except unification.UnificationError:
                    msg = 'Cannot unify types for atoms %s.' \
                        % ' and '.join([str(atom) for atom in atoms])
                    raise unification.UnificationError(msg)

    def unify(self, term):
        for key, value in self.get_substitutions().iteritems():
            term = substitute_type(term, value, key)
        return term

    def get_substitutions(self):
        return self.unifier.get_substitutions()

def unify_types(terms):
    unifier = TermTypeUnifier()
    unifier.add_terms(terms)
    return [unifier.unify(term) for term in terms]
    
    

class Constant(object):
    def __init__(self, name, qtype_):
        self.name = name
        self.qtype = qtype_

    def __repr__(self):
        return 'Constant(%r, %r)' % (self.name, self.qtype)

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.name == other.name
                and self.qtype == other.qtype)

    def __ne__(self, other):
        return not self == other
    
class Variable(object):
    def __init__(self, name, qtype_):
        self.name = name
        self.qtype = qtype_

    def __repr__(self):
        return 'Variable(%r, %r)' % (self.name, self.qtype)
    
    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.name == other.name
                and self.qtype == other.qtype)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.__class__) ^ hash(self.name) ^ hash(self.qtype)

class Combination(object):
    def beta_reduce(self):
        if is_abstraction(self.operator):
            return substitute(self.operator.body,
                              self.operand,
                              self.operator.bound)
        return self

    @staticmethod
    def infer_types(operator, operand):
        if operator.qtype.is_variable:
            operator = substitute_type(operator,
                                       qtype.qfun(qtype.qvar(), qtype.qvar()),
                                       operator.qtype)

        if operator.qtype.name != 'fun':
            raise qtype.UnificationError('Operators must be functions.')

        unifier = qtype.TypeUnifier()
        unifier.add_types([operator.qtype.args[0], operand.qtype])
        for key, value in unifier.get_substitutions().iteritems():
            operator = substitute_type(operator, value, key)
            operand = substitute_type(operand, value, key)

        operator, operand = unify_types([operator, operand])
        
        if operator.qtype.args[0] != operand.qtype:
            message = ('Combination operand type must match'
                       ' operator argument type. Operand %r does not match'
                       ' operator %r.' % (operand, operator))
            raise qtype.UnificationError(message)

        return operator, operand
        
    def __init__(self, operator, operand):
        self.operator, self.operand = self.infer_types(operator, operand)

    @property
    def qtype(self):
        return self.operator.qtype.args[1]
    
    def __repr__(self):
        return 'Combination(%r, %r)' % (self.operator, self.operand)
    
    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.operator == other.operator
                and self.operand == other.operand)

    def __ne__(self, other):
        return not self == other

class Abstraction(object):
    @staticmethod
    def infer_types(bound, body):
        return unify_types([bound, body])
    
    def __init__(self, bound, body):
        self.bound, self.body = self.infer_types(bound, body)
        
        if not is_variable(self.bound):
            raise qtype.UnificationError('Bound terms must be variables.')

    @property
    def qtype(self):
        return qtype.qfun(self.bound.qtype, self.body.qtype)
    
    def __repr__(self):
        return 'Abstraction(%r, %r)' % (self.bound, self.body)

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.bound == other.bound
                and self.body == other.body)

    def __ne__(self, other):
        return not self == other

def unary_op(op, a):
    return Combination(op, a)

def binary_op(op, a, b):
    return Combination(Combination(op, a), b)

def binder(op, x, a):
    return unary_op(op, Abstraction(x, a))
