constant('not:bool->bool')
operator('not', 1, 'right', 100)

constant('or:bool->bool->bool')
operator('or', 2, 'left', 300)

constant('and:bool->bool->bool')
operator('and', 2, 'left', 200)
definition(r'(and) = (\x.\y.(not ((not x) or (not y))))')

constant('implies:bool->bool->bool')
operator('implies', 2, 'left', 300)
definition(r'(implies) = (\x.\y.((not x) or y))')

constant('iff:bool->bool->bool')
operator('iff', 2, 'left', 400)
definition(r'(iff) = (\x.\y.((x implies y) and (y implies x)))')

constant('=:?a->?a->bool')
operator('=', 2, 'left', 500)

constant('schema:((obj->bool)->bool)->bool')
binder('schema')

constant('for_all:(obj->bool)->bool')
binder('for_all')

constant('exists:(obj->bool)->bool')
binder('exists')
definition(r'(exists) = (\x.(not (for_all y . (not (x(y))))))')
