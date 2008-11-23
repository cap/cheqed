from cheqed.core import qterm
from cheqed.core.term_type_unifier import unify_types

class Sequent(object):
    def __init__(self, left=[], right=[]):
        self._left, self._right = self.infer_types(left[:], right[:])
        self._left = list(self._left)
        self._right = list(self._right)

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

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
        free = set()
        for term in self.left + self.right:
            free.update(term.free_variables())
        return free
