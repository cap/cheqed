constant('in:obj->obj->bool')
constant('subset:obj->obj->bool')

operator('in', 2, 'left', 50)
operator('subset', 2, 'left', 50)

# axioms
axiom('set.extensionality',
      r'(for_all x . for_all y . for_all z .'
      r'((z in x) iff (z in y))) implies (x = y)')

axiom('set.unordered_pair',
      r'for_all x . for_all y . for_all z .'
      r'(z in unordered_pair(x, y)) iff ((z = x) or (z = y))')

axiom('set.powerset',
      r'for_all x . for_all y .'
      r'(y in powerset(x)) iff (y subset x)')

axiom('set.family_union',
      r'for_all F . for_all x .'
      r'(x in family_union(F)) iff (exists y . (y in F) and (x in y))')

axiom('set.separation',
      r'schema phi . for_all X . for_all y .'
      r'(y in separation(X, phi)) iff ((y in X) and phi(y))')

# y in { x | x in X and phi } iff (y in X and s/y/x/phi)

axiom('set.infinity',
      r'exists x . (emptyset in x) and '
      r'(for_all y . (y in x) implies (successor(y) in x))')

# definitions
definition(r'emptyset = separation(x, (\y not (y in x)))')

definition(r'singleton = (\x . unordered_pair(x, x))')

definition(r'union = (\x \y . family_union(unordered_pair(x, y)))')

definition(r'successor = (\x . union(x, singleton(x)))')

definition(r'(subset) = (\x \y . for_all z . (z in x) implies (z in y))')

definition(r'ordered_pair = (\x \y unordered_pair(singleton(x), unordered_pair(x, y)))')

definition(r'is_in_ordered_pair_first = (\x \y . exists z . (singleton(z) in x) and (y in z))')

definition(r'ordered_pair_first = (\x . separation(y, is_in_ordered_pair_first(x)))')
