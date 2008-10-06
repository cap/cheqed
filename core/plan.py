# I believe that this is just a nice wrapper on a fragment of the
# lambda calculus, with mapping roughly as follows:
#
# Assumption -> Identity Combinator
# Compound -> Variable
# Rule -> Constant
# Branch -> Combination
# Perhaps later this correspondance will allow a clean refactoring.
#
# Even now, we could restrict usage so that Compounds, Rules, and
# Assumptions are not permitted as standalone proofs; only branches
# can stand alone.

class Step:
    def __init__(self, result, plan, justification=None, expansion=None):
        self.result = result
        self.plan = plan
        if justification is None:
            justification = []
        self.justification = justification
        if expansion is None:
            expansion = []
        self.expansion = expansion

class Line:
    def __init__(self, plan, indentation=0):
        self.plan = plan
        self.indentation = indentation

    def indent(self):
        return Line(self.plan, self.indentation + 1)

class Plan(object):
    pass

class Assumption(Plan):
    _id_gen = 0

    @classmethod
    def _get_new_id(cls):
        new_id = Assumption._id_gen
        Assumption._id_gen = Assumption._id_gen + 1
        return new_id
        
    def __init__(self):
        self.id = self._get_new_id()

    def normalize(self, goal):
        return self
    
    def assumptions(self):
        return [self]
    
    def replace(self, assumption, prover):
        if self.id == assumption.id:
            return prover
        return self

    def subgoals(self, goal):
        return [goal]

    def pretty_repr(self, term_printer):
        return 'assumption()'

    def get_step(self, goal):
        return Step(goal, self)
    
    def flatten(self):
        return [Line(self)]

class Branch(Plan):
    def __init__(self, first, *branches):
        self.first = first
        self.branches = branches

    def assumptions(self):
        branch_assumptions = []
        for branch in self.branches:
            branch_assumptions.extend(branch.assumptions())
        return branch_assumptions
        
    def replace(self, assumption, prover):
        return Branch(self.first,
                      *[b.replace(assumption, prover) for b in self.branches])
        
    def normalize(self, goal):
        first_subgoals = self.first.subgoals(goal)
        if len(first_subgoals) != len(self.branches):
            raise 'Branch error: number of goals must equal number of branches.'
        normalized_branches = []
        for branch, subgoal in zip(self.branches, first_subgoals):
            normalized_branches.append(branch.normalize(subgoal))
        return Branch(self.first, *normalized_branches)
        
    def subgoals(self, goal):
        first_subgoals = self.first.subgoals(goal)
        if len(first_subgoals) != len(self.branches):
            raise 'Branch error: number of goals must equal number of branches.'
        branch_subgoals = []
        for branch, subgoal in zip(self.branches, first_subgoals):
            branch_subgoals.extend(branch.subgoals(subgoal))
        return branch_subgoals

    def pretty_repr(self, term_printer):
        return ('branch(%s, %s)'
                % (self.first.pretty_repr(term_printer),
                   ', '.join([branch.pretty_repr(term_printer)
                              for branch in self.branches])))

    def get_step(self, goal):
        first_subgoals = self.first.subgoals(goal)
        if len(first_subgoals) != len(self.branches):
            raise 'Branch error: number of goals must equal number of branches.'
        branch_steps = []
        for branch, subgoal in zip(self.branches, first_subgoals):
            branch_steps.append(branch.get_step(subgoal))
        
        return Step(goal, self.first, branch_steps)

    def flatten(self):
        lines = [Line(self.first)]
        if len(self.branches) == 1:
            lines.extend(self.branches[0].flatten())
        else:
            for branch in self.branches:
                lines.extend([line.indent() for line in branch.flatten()])
        return lines
            
class Compound(Plan):
    def __init__(self, func, pretty):
        self.func = func
        self.pretty = pretty

    def assumptions(self):
        return []
        
    def replace(self, assumption, prover):
        return self
        
    def expand(self, goal):
        return self.func(goal)
    
    def normalize(self, goal):
        subgoal_count = len(self.subgoals(goal))
        if subgoal_count == 0:
            return self
        return Branch(self, *[Assumption() for i in range(subgoal_count)])
        
    def subgoals(self, goal):
        return self.expand(goal).subgoals(goal)

    def pretty_repr(self, term_printer):
        try:
            return self.pretty(term_printer)
        except TypeError:
            return self.pretty

    def get_step(self, goal):
        return Step(goal, self, expansion=self.expand(goal).get_step(goal))

    def flatten(self):
        return [Line(self)]


class Rule(Plan):
    def __init__(self, func, pretty):
        self.func = func
        self.pretty = pretty

    def assumptions(self):
        return []

    def replace(self, assumption, prover):
        return self
        
    def normalize(self, goal):
        subgoal_count = len(self.subgoals(goal))
        if subgoal_count == 0:
            return self
        return Branch(self, *[Assumption() for i in range(subgoal_count)])
        
    def subgoals(self, goal):
        return self.func(goal)

    def pretty_repr(self, term_printer):
        try:
            return self.pretty(term_printer)
        except TypeError:
            return self.pretty

    def get_step(self, goal):
        return Step(goal, self)

    def flatten(self):
        return [Line(self)]

def walk(proof, walker):
    limb = []
    node = proof
    while isinstance(node, Branch):
        walker.emit(node.first)
        if len(node.branches) == 1:
            node = node.branches[0]
        else:
            for branch in node.branches:
                walker.begin_branch()
                walk(branch, walker)
                walker.end_branch()
            break
    if not isinstance(node, Branch):
        walker.emit(node)

def trace(plan, goal, walker):
    if isinstance(plan, Rule) \
            or isinstance(plan, Compound) \
            or isinstance(plan, Assumption):
        walker.emit_step(plan, goal)
        return plan.subgoals(goal)
    elif isinstance(plan, Branch):
        subgoals = trace(plan.first, goal, walker)
        branches = zip(plan.branches, subgoals)
        if len(branches) == 1:
            return trace(branches[0][0], branches[0][1], walker)
        else:
            result = []
            for branch, subgoal in branches:
                walker.begin_branch()
                result.extend(trace(branch, subgoal, walker))
                walker.end_branch()            
            return result
    else:
        raise Exception('unrecognized plan type')
        
def compress(proof):
    limb = []
    node = proof
    while isinstance(node, Branch):
        limb.append(node.first)
        if len(node.branches) == 1:
            node = node.branches[0]
        else:
            limb.extend([compress(branch) for branch in node.branches])
            break

    if not isinstance(node, Branch):
        limb.append(node)

    return limb
