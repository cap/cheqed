from django import template
register = template.Library()

import cheqed.core

@register.inclusion_tag('sequent_line.html', takes_context=True)
def sequent_line(context, line, side, index):
    node = context['proof'][line]
    side = cheqed.core.side.Side(str(side))
    sequent = node.bottom[0].sequent()
    rules = []
    if node.rule.name == "Hypothesis":
        rules = cheqed.core.proof.specific_applicable_rules(sequent, side, index)
        for rule in rules:
            rule.requires_witness = hasattr(rule, 'witness_class')

    return {
        'idea_id': context['idea_id'],
        'proof_line': line,
        'sequent_side': side,
        'sequent_line': index,
        'formula': str(sequent[side][index]),
        'rules': rules,
        }
