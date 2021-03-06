from nose.tools import assert_true, assert_equal, assert_raises

from cheqed.core.qtype import qvar, qobj, qbool, qfun
from cheqed.core.qtype_unifier import unify
from cheqed.core.unification import UnificationError

def test_str():
    assert str(qobj()) == 'obj'
    assert str(qbool()) == 'bool'
    assert str(qfun(qobj(), qbool())) == '(obj->bool)'
    assert str(qfun(qobj(), qbool())) == '(obj->bool)'
    assert (str(qfun(qfun(qobj(), qobj()), qbool()))
            == '((obj->obj)->bool)')

# def test_make_unifier():
#     var = qvar()
#     obj = qobj()
#     uni = qtype.make_unifier([var, obj])
#     assert uni.apply(var) == obj

#     fun0 = qfun(qobj(), qbool())
#     fun1 = qfun(qvar(), qbool())
#     uni = qtype.make_unifier([fun0, fun1])
#     assert uni.apply(fun1) == fun0

#     fun0 = qfun(qobj(), qbool())
#     fun1 = qfun(qvar(), qbool())
#     uni = qtype.make_unifier([fun0, fun1])
#     assert uni.apply(fun1) == fun0

#     fun2 = qfun(var, var)
#     uni = qtype.make_unifier([fun0, fun2])
#     raises(qtype.UnificationError, uni.apply, fun2)

#     raises(qtype.UnificationError, qtype.make_unifier, [fun0, obj])

#     fun0 = qfun(qobj(), qvar())
#     fun1 = qfun(qvar(), qbool())
#     uni = qtype.make_unifier([fun0, fun1])
#     assert uni.apply(fun0) == uni.apply(fun1)
    
def test_unify():
    assert_raises(UnificationError, unify, [qobj(), qbool()])
    assert_equal(unify([qobj(), qobj()]), qobj())
    assert_equal(unify([qvar(), qobj()]), qobj())
    assert_equal(unify([qobj(), qvar()]), qobj())

    v1 = qvar()
    v2 = qvar()
    uni = unify([v1, v2])
    assert_true(uni == v1 or uni == v2)

    f1 = qfun(qobj(), qbool())
    f2 = qfun(qobj(), qobj())
    f3 = qfun(qvar(), qobj())
    f4 = qfun(qvar(), qvar())

    assert_raises(UnificationError, unify, [f1, f2])
    assert_equal(unify([f2, f3]), f2)
    assert_equal(unify([f2, f4]), f2)
    assert_equal(unify([f3, f4]), f3)

def test_unfiy_tricky():
    v1 = qvar()
    v2 = qvar()
    g1 = qfun(v1, v2)
    g2 = qfun(v2, qobj())

    assert_equal(unify([g1, g2]), qfun(qobj(), qobj()))
