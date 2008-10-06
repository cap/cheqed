import re

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response

from cheqed.core import environment, sequent, prover as prv, plan
from cheqed.core.rules import registry

from models import Plan, Proof, Definition


def proof_start(request):
    goal_text = request.POST['goal']
    goal_term = pt(str(goal_text))
    goal_seq = sequent.Sequent([], [goal_term])

    plan = Plan()
    plan.text = prv.assumption().normalize(goal_seq).pretty_repr(env.printer)
    plan.save()
    
    proof = Proof()
    proof.plan = plan
    proof.goal = prt(goal_term)
    proof.save()

    return HttpResponseRedirect(reverse(proof_detail,
                                        args=[proof.id]))

class Walker:
    def __init__(self):
        self.lines = []

    def begin_branch(self):
        self.lines.append('begin_branch')

    def end_branch(self):
        self.lines.append('end_branch')

    def emit(self, rule):
        self.lines.append(rule.pretty_repr(env.printer))

    def emit_step(self, p, sequent):
        line = {'plan': p.pretty_repr(env.printer),
                'sequent': pr(sequent)}
        if isinstance(p, plan.Assumption):
            line['assumption'] = True
            line['rules'] = prv.applicable_rules(p, sequent)
        self.lines.append(line)

def proof_detail(request, proof_id):
    proof = Proof.objects.get(id=proof_id)
    proof_plan = prv.evaluate(str(proof.plan.text))
    proof_goal = sequent.Sequent([], [pt(str(proof.goal))])
    walker = Walker()
    plan.trace(proof_plan, proof_goal, walker)
    index = 0
    for line in walker.lines:
        if hasattr(line, 'get') and line.get('assumption', False):
            line['assumption_index'] = index
            index += 1

    return render_to_response('proof.html',
                              {'proof': proof,
                               'lines': walker.lines})

def proof_advance(request, proof_id):
    assert request.method == 'POST'
    proof = Proof.objects.get(id=proof_id)
    proof_plan = prv.evaluate(str(proof.plan.text))
    proof_goal = sequent.Sequent([], [pt(str(proof.goal))])
    
    rule = str(request.POST['apply_rule'])
    assumption_index = int(request.POST['assumption_index'])
    kwargs = {}
    for item in request.POST:
        match = re.match(rule + r'\_([a-zA-Z]+)', item)
        print 'matching', item
        if match:
            name = match.group(1)
            try:
                if name == 'witness':
                    value = "parse(r'%s')" % str(request.POST[item])
                elif name == 'index':
                    value = int(request.POST[item])
                elif name == 'name':
                    value = repr(str(request.POST[item]))
            except Exception, e:
                error = str(e)
                break
            kwargs[str(name)] = value
    try:
        assert len(kwargs) <= 1
        code = ''
        if len(kwargs) == 0:
            code = '%s()' % rule
        else:
            code = '%s(%s)' % (rule, kwargs.values()[0])

        node = prv.evaluate(code)
        proof_plan = proof_plan.replace(proof_plan.assumptions()[assumption_index], node)
        proof.plan.text = proof_plan.normalize(proof_goal).pretty_repr(env.printer)
        proof.plan.save()
    except Exception, e:
        error = str(e)
        raise

    return HttpResponseRedirect(reverse(proof_detail,
                                        args=[proof_id]))
    

env = prv.env
pt = env.parser.parse
pr = env.printer.sequent
prt = env.printer.term

def index(request):
    definitions = Definition.objects.all()
    proofs = Proof.objects.all()
    return render_to_response('index.html',
                              {'definitions': definitions,
                               'proofs': proofs})

def parser(request):
    terms = \
'''
x
f(x)
f(g(x), g, x)
f(f)
x:obj
f:obj->obj
f(x:obj, x:bool)
f:obj->bool(x)
not a
a or b
for_all x . phi(x)
phi(x) or x
'''

    results = []
    if request.GET:
        terms = str(request.GET['terms'])
        for term in terms.splitlines():
            try:
                parsed = pt(term)
                result = repr(parsed)
                pretty = prt(parsed)
            except Exception, e:
                result = str(e)
                pretty = ''
            results.append((term, result, pretty))

    context = Context({
        'terms': terms,
        'results': results,
        })
    template = loader.get_template('parser.html')
    return HttpResponse(template.render(context))

def make_pretty_proof(proof):
    lines = proof.flatten()
    for line in lines:
        line.pretty = line.plan.pretty_repr(env.printer)
        line.spaces = range(line.indentation * 4)
    return lines

def real_prover(request):
    if 'reset' in request.GET:
        del request.session['proof']; del request.session['goal']
    error = ''
    prf = None
    if 'proof' in request.session:
        prf = prv.evaluate(str(request.session['proof']))
    goal = None
    if 'goal' in request.session:
        goal = pt(str(request.session['goal']))
        goal_seq = sequent.Sequent([], [goal])
        
    if request.POST:
        if 'start_over' in request.POST:
            try:
                goal = pt(str(request.POST['goal']))
                goal_seq = sequent.Sequent([], [goal])
                prf = prv.assumption().normalize(goal_seq)
            except Exception, e:
                error = str(e)
        elif 'apply_rule' in request.POST:
            rule = str(request.POST['apply_rule'])
            kwargs = {}
            for item in request.POST:
                match = re.match(rule + r'\_([a-zA-Z]+)', item)
                if match:
                    name = match.group(1)
                    try:
                        if name == 'witness':
                            value = "parse(r'%s')" % str(request.POST[item])
                        elif name == 'index':
                            value = int(request.POST[item])
                        elif name == 'name':
                            value = repr(str(request.POST[item]))
                    except Exception, e:
                        error = str(e)
                        break
                    kwargs[str(name)] = value
            try:
                assert len(kwargs) <= 1
                code = ''
                if len(kwargs) == 0:
                    code = '%s()' % rule
                else:
                    code = '%s(%s)' % (rule, kwargs.values()[0])

                node = prv.evaluate(code)
                prf = prf.replace(prf.assumptions()[0], node).normalize(goal_seq)
            except Exception, e:
                error = str(e)

    rules = []
    goals = []
    if prf is not None:
        rules = prv.applicable_rules(prf, goal_seq)
        try:
            for gl in prf.subgoals(goal_seq):
                ppseq = {'left':[], 'right':[]}
                for term in gl.left:
                    ppterm = {'pretty': prt(term),
                              'repr': repr(term),}
                    ppseq['left'].append(ppterm)
                for term in gl.right:
                    ppterm = {'pretty': prt(term),
                              'repr': repr(term),}
                    ppseq['right'].append(ppterm)
                    
                goals.append(ppseq)
        except Exception, e:
            error = str(e)

    if prf is not None:
        request.session['proof'] = prf.pretty_repr(env.printer)
        
    if goal is not None:
        request.session['goal'] = prt(goal)

    walker = Walker()
    plan.trace(prf, goal_seq, walker)
        
    serialized = None
    pretty_proof = None
    if prf is not None and goal is not None:
        serialized = prt(goal) + "..." + prf.pretty_repr(env.printer)
        pretty_proof = make_pretty_proof(prf)

    serialized = repr(plan.compress(prf))
        
    context = Context(
        {'rules': sorted(rules),
         'error': error,
         'goals': goals,
         'proof': serialized,
         'pretty_proof': pretty_proof,
         'tree_view': walker.lines,
         })
    template = loader.get_template('prover.html')
    return HttpResponse(template.render(context))

#import cProfile

def prover(request):
#    cProfile.runctx('real_prover(request)', globals(), locals(), 'web_profile')
    return real_prover(request)

def definitions(request):
    defs = []
    for name, term in env.definitions.iteritems():
        defs.append((name, prt(term)))
    defs.sort()

    axioms = []
    for name, term in env.axioms.iteritems():
        axioms.append((name, prt(term)))
    axioms.sort()

    context = Context({
        'definitions': defs,
        'axioms': axioms,
        })
    template = loader.get_template('definitions.html')
    return HttpResponse(template.render(context))

def rules(request):
    rules = []
    for func in registry.rules:
        rules.append((func.func_name, ''))
    rules.sort()

    context = Context({
        'rules': rules,
        })
    template = loader.get_template('rules.html')
    return HttpResponse(template.render(context))
