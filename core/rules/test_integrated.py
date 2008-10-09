from nose.tools import assert_equal

from cheqed.core import environment, trace, sequent

class TestRules:
    @classmethod
    def setup_class(cls):
        cls.env = environment.load_modules('logic', 'set')
        cls.env.load_extension(open('/home/cap/thesis/cheqed/core/rules/integrated_structural.py'))
        cls.env.load_extension(open('/home/cap/thesis/cheqed/core/rules/integrated_logical_primitive.py'))
        cls.env.load_extension(open('/home/cap/thesis/cheqed/core/rules/integrated_logical_compound.py'))
        cls.env.load_extension(open('/home/cap/thesis/cheqed/core/rules/integrated.py'))

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
        
    def test_foo(self):
        term = self.env.parse('a or not a')
        seq = sequent.Sequent([], [term])

        rule = self.env.rules['excluded_middle']()

        rule.evaluate(seq)
        print self.env.print_proof(rule)

        expanded = rule.expand(seq)
        print self.env.print_proof(expanded)
