from cheqed.core import environment

env = environment.load_modules('logic', 'set')
env.load_plan('cheqed.core.rules.structural')
env.load_plan('cheqed.core.rules.logical')
env.load_plan('cheqed.core.rules.compound')
