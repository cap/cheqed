constant('in:obj->obj->bool')
operator('in', 2, 'left', 50)

constant('subset:obj->obj->bool')
operator('subset', 2, 'left', 50)


# axioms
axiom('set.extensionality',
      r'for_all x . for_all y . for_all z .'
      r'((z in x) iff (z in y)) implies (x = y)')

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
      r'schema phi . for_all x . for_all y .'
      r'(y in separation(x, phi)) iff ((y in x) and phi(y))')

axiom('set.infinity',
      r'exists x . (emptyset in x) and '
      r'(for_all y . (y in x) implies (successor(y) in x))')


# definitions
definition(r'emptyset = separation(x, (\y not (y in x)))')

definition(r'singleton = (\x . unordered_pair(x, x))')

definition(r'union = (\x \y . family_union(unordered_pair(x, y)))')

definition(r'successor = (\x . union(x, singleton(x)))')

definition(r'(subset) = (\x \y . for_all z . (z in x) implies (z in y))')

definition(r'ordered_pair = (\x \y unordered_pair(x, unordered_pair(x, y)))')

definition(r'is_ordered_pair = (\x \y . exists z . z = ordered_pair(x, y))')

definition(r'is_ordered_pair_first'
           r'= (\x \y . is_ordered_pair(x) and (y in x))')

definition(r'is_ordered_pair_second'
           r'= (\x \y . is_ordered_pair(x)'
           r'and (exists z . unordered_pair(y, z) in x))')

definition(r'ordered_pair_first ='
           r'(\x . separation(x, is_ordered_pair_first(x)))')

definition(r'ordered_pair_second ='
           r'(\x . separation(x, is_ordered_pair_second(x)))')
