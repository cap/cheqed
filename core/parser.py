import itertools
import sys

import ply.lex as lex
import ply.yacc as yacc

from cheqed.core import qterm, qtype

class SyntaxError(Exception):
    pass

class PrecedenceError(Exception):
    pass

class Parser:
    def __init__(self, syntax, term_builder, quiet=True):
        self.tokens = [
            'LPAREN', 'RPAREN',
            'COMMA',
            'IDENT',
            'DOT',
            'BSLASH',
            'ARROW',
            'COLON',
            'QMARK',
            'NEVERMATCH',
            ]

        self.syntax = syntax
        self.term_builder = term_builder

        self._make_atomic_type()
        self._make_unary_operator()
        self._make_binary_operator()
        self._make_binder()
        self._make_prefix_constants()

        for word in self.syntax.words():
            self.tokens.append(word.token)

        precedence = [
            (5000, 'nonassoc', 'DOT'),
            (4900, 'nonassoc', 'BSLASH'),
            (4800, 'right', 'ARROW'),
            (0, 'nonassoc', 'LPAREN'),
            (0, 'nonassoc', 'RPAREN'),
            ]
                
        precedence.extend([(o.precedence, o.associativity, o.token)
                           for o in self.syntax.operators()])

        precedence.sort(reverse=True)

        self.precedence = []
        for key, group in itertools.groupby(precedence, lambda p: p[0]):
            token = group.next()
            entry = [token[1], token[2]]
            for token in group:
                self.check_associativities(entry, token)
                entry.append(token[2])
            self.precedence.append(entry)

        if quiet:
            stderr = sys.stderr
            sys.stderr = open('/dev/null', 'w')
        try:
            self.lexer = lex.lex(module=self)
            self.parser = yacc.yacc(module=self, start='term',
                                    debug=0, write_tables=0)
            self.type_parser = yacc.yacc(module=self, start='type',
                                         debug=0, write_tables=0)
        finally:
            if quiet:
                sys.stderr = stderr

    
    def _make_doc(self, nonterminal, pattern, words):
        if len(words) > 0:
            tokens = [word.token for word in words]
            productions = '\n| '.join([pattern % tok for tok in tokens])
            return '%s : %s' % (nonterminal, productions)
        else:
            return '%s : NEVERMATCH' % nonterminal
        
    def _make_binary_operator(self):
        def p_binary_operator(p):
            p[0] = self.term_builder.build_binary_op(self.syntax[p[2]].constant, p[1], p[3])

        words = [word for word in self.syntax.operators()
                 if word.arity == 2]
        
        doc = self._make_doc('binary_operator', 'term %s term', words)
        p_binary_operator.__doc__ = doc
        self.p_binary_operator = p_binary_operator

    def _make_unary_operator(self):
        def p_unary_operator(p):
            p[0] = self.term_builder.build_combination(self.syntax[p[1]].constant, p[2])

        words = [word for word in self.syntax.operators()
                 if word.arity == 1]
        
        doc = self._make_doc('unary_operator', '%s term', words)
        p_unary_operator.__doc__ = doc
        self.p_unary_operator = p_unary_operator

    def _make_binder(self):
        def p_binder(p):
            p[0] = self.term_builder.build_combination(self.syntax[p[1]].constant,
                                  self.term_builder.build_abstraction(p[2], p[3]))

        doc = self._make_doc('binder', '%s atom term',
                             self.syntax.binders())
        p_binder.__doc__ = doc
        self.p_binder = p_binder

    def _make_prefix_constants(self):
        def p_prefix_constant(p):
            p[0] = self.syntax[p[2]].constant
            
        doc = self._make_doc('prefix_constant', 'LPAREN %s RPAREN',
                             self.syntax.words())
        p_prefix_constant.__doc__ = doc
        self.p_prefix_constant = p_prefix_constant

    def _make_atomic_type(self):
        def p_atomic_type(p):
            p[0] = self.syntax[p[1]].constructor()

        doc = self._make_doc('atomic_type', '%s', self.syntax.types())
        p_atomic_type.__doc__ = doc
        self.p_atomic_type = p_atomic_type

    @staticmethod
    def check_associativities(entry, token):
        if entry[0] != token[1]:
            message = ('Tokens at the same precedence level must have the'
                       ' same associativities. %s and %s have precedence'
                       ' %d but associativities %s and %s.'
                       % (entry[1], token[2], token[0],
                          entry[0], token[1]))
            raise PrecedenceError(message)
        

    t_QMARK = r'\?'
    t_DOT = r'\.'
    t_BSLASH = r'\\'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COMMA = r','
    t_ARROW = r'->'
    t_COLON = r':'
    t_NEVERMATCH = r'never match anything please'

    def t_IDENT(self, t):
        r'=|[a-zA-Z_]+'
        try:
            t.type = self.syntax[t.value].token
        except KeyError:
            t.type = 'IDENT'
        return t

    t_ignore = ' \t'

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        raise SyntaxError("Syntax error at '%s'" % t.value[0])

    def p_term(self, p):
        '''term : atom
                | combination
                | abstraction
                | binary_operator
                | unary_operator
                | binder
                | prefix_constant
                | dot_term'''
        p[0] = p[1]

    def p_dot_term(self, p):
        'dot_term : DOT term'
        p[0] = p[2]

    def p_term_paren(self, p):
        'term : LPAREN term RPAREN'
        p[0] = p[2]

    def p_atom(self, p):
        'atom : IDENT'
        p[0] = self.term_builder.build_variable(p[1], qtype.qvar())

    def p_typed_atom(self, p):
        'atom : IDENT COLON type'
        p[0] = self.term_builder.build_variable(p[1], p[3])

    def p_atomic_type_type(self, p):
        'type : atomic_type'
        p[0] = p[1]

    def p_atomic_variable_type(self, p):
        'atomic_type : QMARK IDENT'
        if p[2] not in self.type_context:
            self.type_context[p[2]] = qtype.qvar()
        p[0] = self.type_context[p[2]]
        
    def p_function_type(self, p):
        'type : type ARROW type'
        p[0] = qtype.qfun(p[1], p[3])

    def p_paren_type(self, p):
        'type : LPAREN type RPAREN'
        p[0] = p[2]
        
    def p_abstraction(self, p):
        'abstraction : BSLASH atom term'
        p[0] = self.term_builder.build_abstraction(p[2], p[3])

    def p_arglist_empty(self, p):
        'arglist :'
        p[0] = []

    def p_arglist_pair(self, p):
        'arglist : term COMMA arglist'
        p[0] = [p[1]] + p[3]

    def p_arglist_term(self, p):
        'arglist : term'
        p[0] = [p[1]]

    def p_combination(self, p):
        'combination : term LPAREN arglist RPAREN'
        c = p[1]
        a = p[3]
        a.reverse()
        while a:
            c = self.term_builder.build_combination(c, a.pop())
        p[0] = c

    def p_error(self, p):
        raise SyntaxError("Syntax error at '%s'" % p.value)

    def parse(self, string):
        self.type_context = {}
        term = self.parser.parse(string, lexer=self.lexer)
        self.type_context = None
        return term

    def parse_type(self, string):
        self.type_context = {}
        term = self.type_parser.parse(string, lexer=self.lexer)
        self.type_context = None
        return term
