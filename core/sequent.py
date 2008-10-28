from cheqed.core import qterm
from cheqed.core.term_type_unifier import unify_types

class Sequent:
    def __init__(self, left=[], right=[]):
        self.left, self.right = self.infer_types(left[:], right[:])

    def __getitem__(self, key):
        if key == 'left':
            return self.left
        elif key == 'right':
            return self.right
        else:
            raise KeyError

    @staticmethod
    def infer_types(left, right):
        all = left + right
        if len(all) > 1:
            all = unify_types(all)
            left = all[:len(left)]
            right = all[len(left):]
        return left, right

    def __repr__(self):
        return 'Sequent(%r, %r)' % (self.left, self.right)

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.left == other.left
                and self.right == other.right)

    def free_variables(self):
        return reduce(lambda x, y: x.union(y),
                      map(lambda f: qterm.free_variables(f),
                          self.left + self.right))
