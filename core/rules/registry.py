import inspect

from cheqed.core.plan import Compound, Rule
#from cheqed.core.rules.match import match_first

rules = []

def register(func):
    arg_names, varargs, varkw, defaults = inspect.getargspec(func)

    if not hasattr(func, 'arg_names'):
        func.arg_names = arg_names

    func.is_registered = True
    
    rules.append(func)
    return func

def applicable(side, pattern):
    def is_applicable(environment, sequent):
        try:
            environment.match_first(sequent, side, pattern)
            return True
        except:
            return False
        
    def decorator(fun):
        fun.is_applicable = is_applicable
        return fun

    return decorator

def rule(func, repr_):
    return Rule(func, repr_)

def make_compound(func):
    arg_names, varargs, varkw, defaults = inspect.getargspec(func)
    arg_names.remove('goal')
    assert varargs is None
    assert varkw is None
    assert defaults is None

    def new_func(*args):
        def prettifier(printer):
            pretty_args = []
            for arg, name in zip(args, arg_names):
                if name == 'witness':
                    pretty_args.append("parse(r'%s')" % printer.term(arg))
                elif name == 'index':
                    pretty_args.append(str(arg))
                elif name == 'name':
                    pretty_args.append(repr(arg))
                else:
                    raise 'Unrecognized compound argument'
            return '%s(%s)' % (func.func_name, ', '.join(pretty_args))
                
        return Compound(lambda goal: func(goal, *args), prettifier)

    new_func.func_name = func.func_name
    new_func.arg_names = arg_names

    return new_func
