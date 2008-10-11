from nose.tools import assert_equal

from cheqed.core import environment, trace, sequent

class TestRules:
    @classmethod
    def setup_class(cls):
        cls.env = environment.make_default()

    def test_left_negation(self):
        term = self.env.parse('not a')
        seq = sequent.Sequent([term], [])
        rule = self.env.rules['left_negation']()
        result = rule.evaluate(seq)
        goal = [sequent.Sequent([], [self.env.parse('a:bool')])]
        assert_equal(result, goal)

    def test_right_negation(self):
        term = self.env.parse('not a')
        seq = sequent.Sequent([], [term])
        rule = self.env.rules['right_negation']()
        result = rule.evaluate(seq)
        goal = [sequent.Sequent([self.env.parse('a:bool')], [])]
        assert_equal(result, goal)

    def test_left_conjunction(self):
        term = self.env.parse('a and b')
        seq = sequent.Sequent([term], [])
        rule = self.env.rules['left_conjunction']()
        result = rule.evaluate(seq)
        goal = [sequent.Sequent([self.env.parse('a:bool'),
                                 self.env.parse('b:bool')],
                                [])]
        assert_equal(result, goal)

    def test_right_conjunction(self):
        term = self.env.parse('a and b')
        seq = sequent.Sequent([], [term])
        rule = self.env.rules['right_conjunction']()
        result = rule.evaluate(seq)
        goal = [sequent.Sequent([], [self.env.parse('a:bool')]),
                sequent.Sequent([], [self.env.parse('b:bool')])]
        assert_equal(result, goal)
