import re

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response

from cheqed.core import environment, sequent, trace

from models import Plan, Proof, Definition

env = environment.make_default()
for definition in Definition.objects.all():
    env.add_definition(definition.text)

def definition_add(request):
    definition = Definition()
    definition.text = str(request.POST['definition'])

    env.add_definition(definition.text)
    definition.save()
    
    return HttpResponseRedirect(reverse(index))

def proof_start(request):
    goal_text = request.POST['goal']
    goal_term = env.parse(str(goal_text).strip())
    goal_seq = sequent.Sequent([], [goal_term])

    p = Plan()
    assumption = env.rules['assumption']()
    p.text = env.print_proof(assumption)
    p.save()
    
    proof = Proof()
    proof.plan = p
    proof.goal = env.printer.print_term(goal_term)
    proof.save()

    return HttpResponseRedirect(reverse(proof_detail,
                                        args=[proof.id]))

from mako.template import Template
from cStringIO import StringIO

class Walker:
    def __init__(self):
        self.template = Template(filename='/home/cap/thesis/cheqed/app/proof/proof.html', format_exceptions=True)
        self.buffer = StringIO()
        self.assumption_index = 0

    def render(self, name, **kwargs):
        template = self.template.get_def(name)
        self.buffer.write(template.render(**kwargs))

    def unpack_goal(self, goal):
        p_goal = []
        for i in range(max(len(goal.left), len(goal.right))):
            if i < len(goal.left):
                left = env.printer.print_term(goal.left[i])
            else:
                left = ''

            if i < len(goal.right):
                right = env.printer.print_term(goal.right[i])
            else:
                right = ''

            p_goal.append((left, right))
        return p_goal

    def begin_primitive(self, primitive, goal):
        assumption_index = self.assumption_index
        if primitive.func.func_name == 'assumption':
            rules = env.applicable_rules(goal)
            rules.sort(key=lambda x: x.rule_name())
            self.assumption_index += 1
        else:
            rules = []
        p_primitive = env.print_proof(primitive)
        p_goal = self.unpack_goal(goal)
        self.render('begin_primitive',
                    primitive=p_primitive,
                    goal=p_goal,
                    rules=rules,
                    assumption_index=assumption_index)

    def end_primitive(self, primitive):
        self.render('end_primitive')
    
    def begin_compound(self, compound, goal):
        p_compound = env.print_proof(compound)
        p_goal = self.unpack_goal(goal)
        self.render('begin_compound',
                    compound=p_compound,
                    goal=p_goal)

    def end_compound(self, compound):
        self.render('end_compound')

    def begin_branch(self, branch, goal):
        if len(branch.branches) > 1:
            self.render('begin_branch')

    def end_branch(self, branch):
        if len(branch.branches) > 1:
            self.render('end_branch')

def proof_detail(request, proof_id):
    proof = Proof.objects.get(id=proof_id)
    proof_plan = env.evaluate(str(proof.plan.text))
    proof_goal = sequent.Sequent([], [env.parse(str(proof.goal))])
    walker = Walker()
    proof_plan.evaluate(proof_goal, walker)

    return render_to_response('proof.html',
                              {'proof': proof,
                               'tree': walker.buffer.getvalue()})

class AssumptionWalker:
    def __init__(self):
        self.assumptions = []

    def begin_primitive(self, primitive, goal):
        if primitive.func.func_name == 'assumption':
            self.assumptions.append((primitive, goal))

    def end_primitive(self, primitive):
        pass
    
    def begin_compound(self, compound, goal):
        pass
    
    def end_compound(self, compound):
        pass

    def begin_branch(self, branch, goal):
        pass
    
    def end_branch(self, branch):
        pass
    
def proof_advance(request, proof_id):
    assert request.method == 'POST'
    proof = Proof.objects.get(id=proof_id)
    proof_plan = env.evaluate(str(proof.plan.text))
    proof_goal = sequent.Sequent([], [env.parse(str(proof.goal))])

    walker = AssumptionWalker()
    proof_plan.evaluate(proof_goal, walker)
    
    rule_name = str(request.POST['rule_name'])
    args = request.POST.getlist('arg')
    assumption_index = int(request.POST['assumption_index'])

    builder = env.rules[rule_name]
    rule = builder(*args)

    assumption, assumption_goal = walker.assumptions[assumption_index]
    subgoals = rule.evaluate(assumption_goal)
    padding = [env.rules['assumption']() for subgoal in subgoals]
    branch = trace.Branch(rule, *padding)

    proof_plan = proof_plan.replace(assumption, branch)
    proof.plan.text = env.print_proof(proof_plan)
    proof.plan.save()

    return HttpResponseRedirect(reverse(proof_detail,
                                        args=[proof_id]))
    

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
                parsed = env.parse(term)
                result = repr(parsed)
                pretty = env.printer.print_term(parsed)
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

def definitions(request):
    defs = []
    for name, term in env.definitions.iteritems():
        defs.append((name, env.printer.print_term(term)))
    defs.sort()

    axioms = []
    for name, term in env.axioms.iteritems():
        axioms.append((name, env.printer.print_term(term)))
    axioms.sort()

    context = Context({
        'definitions': defs,
        'axioms': axioms,
        })
    template = loader.get_template('definitions.html')
    return HttpResponse(template.render(context))

def rules(request):
    rules = []
    for builder in env.rules.values():
        rules.append((builder.rule_name(), ''))
    rules.sort()

    context = Context({
        'rules': rules,
        })
    template = loader.get_template('rules.html')
    return HttpResponse(template.render(context))
