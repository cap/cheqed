from cheqed.core import environment, qterm

env = environment.load_modules('logic', 'set')

def match_first(sequent, side, string):
    term = sequent[side][0]
    pattern = env.parser.parse(string)
    return qterm.match(pattern, term)

def match_second(sequent, side, string):
    term = sequent[side][1]
    pattern = env.parser.parse(string)
    return qterm.match(pattern, term)
