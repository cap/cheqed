from py.test import raises

from cheqed.core.qtype import qvar, qobj, qbool, qfun
from cheqed.core import qtype

def test_str():
    qobj = qtype.qobj()
    qbool = qtype.qbool()
    
    assert str(qobj) == 'obj'
    assert str(qbool) == 'bool'
    assert str(qtype.qfun(qobj, qbool)) == '(obj->bool)'
    assert str(qtype.qfun(qobj, qbool)) == '(obj->bool)'
    assert (str(qtype.qfun(qtype.qfun(qobj, qobj), qbool))
            == '((obj->obj)->bool)')

def test_make_unifier():
    var = qvar()
    obj = qobj()
    uni = qtype.make_unifier([var, obj])
    assert uni.apply(var) == obj

    fun0 = qfun(qobj(), qbool())
    fun1 = qfun(qvar(), qbool())
    uni = qtype.make_unifier([fun0, fun1])
    assert uni.apply(fun1) == fun0

    fun0 = qfun(qobj(), qbool())
    fun1 = qfun(qvar(), qbool())
    uni = qtype.make_unifier([fun0, fun1])
    assert uni.apply(fun1) == fun0

    fun2 = qfun(var, var)
    uni = qtype.make_unifier([fun0, fun2])
    raises(qtype.UnificationError, uni.apply, fun2)

    raises(qtype.UnificationError, qtype.make_unifier, [fun0, obj])

    fun0 = qfun(qobj(), qvar())
    fun1 = qfun(qvar(), qbool())
    uni = qtype.make_unifier([fun0, fun1])
    assert uni.apply(fun0) == uni.apply(fun1)
    
def test_unify():
    raises(qtype.UnificationError, qobj().unify, qbool())
    assert qobj().unify(qobj()) == qobj()
    assert qvar().unify(qobj()) == qobj()
    assert qobj().unify(qvar()) == qobj()
    v1 = qvar()
    v2 = qvar()
    uni = v1.unify(v2)
    assert uni == v1 or uni == v2

    f1 = qfun(qobj(), qbool())
    f2 = qfun(qobj(), qobj())
    f3 = qfun(qvar(), qobj())
    f4 = qfun(qvar(), qvar())

    raises(qtype.UnificationError, f1.unify, f2)
    assert f2.unify(f3) == f2
    assert f2.unify(f4) == f2
    assert f4.unify(f3) == f3

def test_unfiy_tricky():
    v1 = qvar()
    v2 = qvar()
    g1 = qfun(v1, v2)
    g2 = qfun(v2, qobj())
    assert g1 != g2

    assert qtype.unify([g1, g2]) == qfun(qobj(), qobj())
