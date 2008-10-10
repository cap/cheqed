class NullLog:
    def begin_primitive(self, primitive, goal):
        pass

    def end_primitive(self, primitive):
        pass
    
    def begin_compound(self, compound, goal):
        pass

    def end_compound(self, compound):
        pass

    def begin_branch(self, branch, goal):
        pass

    def end_branch(self, branch):
        pass

class Primitive:
    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def __repr__(self):
        return 'Primitive(%r, %r)' % (self.func, self.args)
    
    def evaluate(self, goal, log=NullLog()):
        log.begin_primitive(self, goal)

        subgoals = self.func(goal, *self.args)

        log.end_primitive(self)
        return subgoals

    def replace(self, a, b):
        if self == a:
            return b
        return self

class Compound:
    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def __repr__(self):
        return 'Compound(%r, %r)' % (self.func, self.args)

    def evaluate(self, goal, log=NullLog()):
        log.begin_compound(self, goal)

        expansion = self.expand(goal)
        subgoals = expansion.evaluate(goal, log)

        log.end_compound(self)
        return subgoals
    
    def expand(self, goal):
        return self.func(goal, *self.args)

    def replace(self, a, b):
        if self == a:
            return b
        return self

class Branch:
    def __init__(self, rule, *branches):
        self.rule = rule
        self.branches = branches

    def __repr__(self):
        return 'Branch(%r, %r)' % (self.rule, self.branches)

    def replace(self, a, b):
        if self == a:
            return b
        return Branch(self.rule.replace(a, b),
                      *[branch.replace(a, b) for branch in self.branches])

    def evaluate(self, goal, log=NullLog()):
        subgoals = self.rule.evaluate(goal, log)
        log.begin_branch(self, goal)

        unmet_goals = []
        for subgoal, branch in zip(subgoals, self.branches):
            unmet_goals.extend(branch.evaluate(subgoal, log))

        log.end_branch(self)
        return unmet_goals

primitive = Primitive
compound = Compound
branch = Branch

def pair(first, second):
    return branch(first, second)

def sequence(*args):
    if len(args) == 1:
        return args[0]
    else:
        return pair(args[0], sequence(*(args[1:])))

# sequence(
#     left_negation(),
#     right_negation(),
#     branch(right_conjunction(),
#            right_universal('x')))

# class Tactical:
#     def __init__(self, func, *args):
#         self.func = func
#         self.args = args

#     def __repr__(self):
#         return 'Tactical(%r, *%r)' % (self.func, self.args)

#     def expand(self, goal):
#         return self.func(*args, goal)

#     def evaluate(self, goal, log=NullLog):
#         expansion = self.expand(goal)
#         return expansion.evaluate(goal, log)

    
#     def trace(self, goal, visitor):
#         subgoals = self.rule.trace(goal, visitor)

#         if len(subgoals) > 1:
#             visitor.begin_branch()

#         subsubgoals = []
#         for subgoal, branch in zip(subgoals, self.branches):
#             subsubgoals.extend(branch.trace(subgoal, visitor))

#         if len(subgoals) > 1:
#             visitor.end_branch()

#         return subsubgoals

    
#     def trace(self, goal, visitor):
#         visitor.emit_step(self, goal)
#         visitor.begin_compound()
#         expansion = self.expand(goal)
#         subgoals = expansion.trace(goal, visitor)
#         visitor.end_compound()
#         return subgoals







#     def expand(self, goal):
#         rule = self.rule.expand(goal)
#         branches = []        

#         subgoals = rule.evaluate(goal)
#         for subgoal, branch in zip(subgoals, self.branches):
#             branches.append(branch.expand(subgoal))

#         return Branch(rule, branches)





    
# class Assumption:
#     def __init__(self, rule):
#         self.rule = rule

#     def __repr__(self):
#         return 'Assumption(%r)' % (self.rule)

#     def simplify(self, goal):
#         subgoals = self.rule.trace(goal)
#         return Branch(self.rule, [None] * len(subgoals))
    
#     def trace(self, goal, visitor):
#         visitor.emit_step(self, goal)
#         return []

    
# class Instantiation:
#     def __init__(self, rule, goal, subgoals):
#         self.rule = rule
#         self.goal = goal
#         self.subgoals = subgoals

    
    

# def trace(proof, goal, rules, visitor):
#     rule = proof[0]
#     if not isinstance(rule, list):
#         rule = [rule]

#     rule_name = rule[0]
#     rule_func = rules[rule_name]

#     visitor.emit_step(rule, goal)
#     if rule_func.is_primitive:
#         subgoals = rule_func(*rule[1:], goal)
#     else:
#         visitor.begin_compound()
#         subproof = rule_func(*rule[1:], goal)
#         subgoals = trace(subproof, goal, rules, visitor)
#         visitor.end_compound()

#     subsubgoals = []
#     if len(subgoals) > 1:
#         visitor.begin_branch()

#     for subgoal, subproof in zip(subgoals, proof[1:]):
#         subsubgoals.extend(trace(subproof, subgoal, rules, visitor))

#     if len(subgoals) > 1:
#         visitor.end_branch()

#     return subsubgoals
