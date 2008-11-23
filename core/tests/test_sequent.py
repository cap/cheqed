from nose.tools import assert_equal, assert_raises

from cheqed.core.sequent import Sequent

class TestSequent:
    def test_immutable(self):
        assert_raises(AttributeError, setattr, Sequent(), 'left', None)
        assert_raises(AttributeError, setattr, Sequent(), 'right', None)
        
