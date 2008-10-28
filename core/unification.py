class UnificationError(Exception):
    pass

class Unifier:
    def __init__(self, is_variable, occurs_in):
        self.is_variable = is_variable
        self.occurs_in = occurs_in
        self.sets = []
        
    def find(self, value):
        for index, (rep, set_) in enumerate(self.sets):
            if value in set_:
                return index

        self.sets.append((value, set([value])))
        return len(self.sets) - 1
    
    def union(self, index_a, index_b):
        if index_a == index_b:
            return
        
        rep_a, set_a = self.sets[index_a]
        rep_b, set_b = self.sets[index_b]
        
        if self.is_variable(rep_a):
            keep = index_b
            discard = index_a
        elif self.is_variable(rep_b):
            keep = index_a
            discard = index_b
        elif rep_a != rep_b:
            raise UnificationError('foo')
        else:
            return

        if self.occurs_in(self.sets[discard][0], self.sets[keep][0]):
            raise UnificationError('bar')
        self.sets[keep][1].update(self.sets[discard][1])
        del self.sets[discard]

    def unify(self, a, b):
        '''Extend the unifier such that a and b will be equivalent after
        applying the resultant substitutions.

        Raise UnificationError if unification is imossible.
        '''
        self.union(self.find(a), self.find(b))

    def get_substitutions(self):
        '''return a dictionary of substitutions (value for key)'''
        result = {}
        for rep, set_ in self.sets:
            for value in set_:
                if value != rep:
                    result[value] = rep
        return result
