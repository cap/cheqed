# helpers
def permute(list_, index):
    return [list_[index]] + list_[:index] + list_[index + 1:]

def contract(list_):
    return [list_[0]] + list_

def weaken(list_):
    return list_[1:]

# rules
@primitive
@arg_types('int')
@applicable(lambda goal: False)
def left_permutation(goal, index):
    return [sequent(permute(goal.left, index), goal.right)]

@primitive
@arg_types('int')
@applicable(lambda goal: False)
def right_permutation(goal, index):
    return [sequent(goal.left, permute(goal.right, index))]

@primitive
@applicable(lambda goal: False)
def left_contraction(goal):
    return [sequent(contract(goal.left), goal.right)]

@primitive
@applicable(lambda goal: False)
def right_contraction(goal):
    return [sequent(goal.left, contract(goal.right))]

@primitive
@applicable(lambda goal: False)
def left_weakening(goal):
    return [sequent(weaken(goal.left), goal.right)]

@primitive
@applicable(lambda goal: False)
def right_weakening(goal):
    return [sequent(goal.left, weaken(goal.right))]
