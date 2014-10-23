import collections.deque as deque

class GasprException(Exception):
    pass

class GaspBuilder(object):
    """Tracks state through the ASP grammar; builds strings."""

    CONS=":-"
    WCONS=":~"
    DOT=".\n"
    AGGR_COUNT="#count"
    AGGR_MAX="#max"
    AGGR_MIN="#min"
    AGGR_SUM="#sum"
    OPT_MIN="#minimize"
    OPT_MAX="#maximize"

    def __init__(self):
        self.todo = deque()
        self.buf = deque()
        self.expect_list = False

    def __str__(self):
        self.buf = [''.join(self.buf)]
        return self.buf[0]

    def __lshift__(self, key):
        if type(key) == list:
            self.todo.extend(key)
        else:
            self.todo.append(key)
        return self

    def __iadd__(self, key):
        if type(key) == list:
            self.buf.extend(key)
        else:
            self.buf.append(key)
        return self

    def word(self, name):
        if len(self.todo) == 0:
            s = str(self)
            if len(s) > 0:
                self.statements.append(s)
            self << self.stmt
        nxt = self.todo.pop(0)
        if type(nxt) == str:
            self += nxt
            self.word(name)
        else:
            nxt(name)

    def call(self, *args):
        joined = ", ".join(str(arg) for arg in args)
        if self.paren_list:
            self += ['(', joined, ')']
        else:
            self += joined
        return self

    def stmt(self, name):
        if name == 'iff':
            self += ':- '
            self.todo.append(body)
        elif name == 'unless':
            self += ':~ '
            self.todo.append(body)
        elif name == 'let':
            self.todo.append(head, ":- ", body)

    def head(self, name):
        self << self.body

    def body(self, name):
        if name == 'neg':
            self += "not "
        self << self.body



class Gaspr(object):
    """Thin front-end DSL to GaspBuilder."""

    def __init__(self):
        self.builder = GaspBuilder()

    def __str__(self):
        return str(self.builder)

    def __iadd__(self, rhs):
        if type(rhs) == list:
            self.buf.extend([str(k) for k in rhs])
        else:
            self.buf.append(str(rhs))
        return self

    def __getattr__(self, name):
        self.builder.word(name)
        return self

    def __call__(self, *args):
        self.builder.call(name)
        return self

    def list(self, delim, items, allow_empty=False):
        if len(items) > 0 or allow_empty:
            self += delim[0]
            self += delim[1].join(items)
            self += delim[2]
        return self

    def term(self, s, *terms):
        self += s
        self.list('(,)', terms)
        return self

    def lit(self, name, *terms):
        self += [name, '(']  # name can start with a "-"
        self += terms
        self += ')'
        return self

    def minimize(self, *elements):
        if len(elements) == 0:
            raise GasprException(
                "minimize requires some optimization elements")
        self += self.MINIMIZE
        self.list('{;}', elements)

    def opt_elt(self, weight_at_level, *nafs):
        self += weight_at_level
        if len(nafs) > 0:
            self += ":"
            self += ", ".join(nafs)
        return self


g = Gaspr()
g.term('host', 'a', 1, 4)
g.term('host', 'b', 2, 4)
g.term('host', 'c', 3, 4)
g.term('host', 'd', 4, 4)

g.term('inst_mem', 1, 1)
g.term('inst_mem', 2, 2)
g.term('inst_mem', 3, 2)

g.term('affinity', 1, 2)
g.term('antiaffinity', 2, 3)
g.term('antiaffinity', 2, 3)
g.term('host_cap', 'a', 'sriov')
g.term('inst_cap', 1, 'sriov')

g.let(g.term('host', 'H')).iff(g.term('host', 'H', '_', '_'))
g.let(g.term('host_ord', 'H', 'O')).iff(g.term('host', 'H', 'O', '_'))
g.let(g.term('host_mem', 'H', 'F')).iff(g.term('host', 'H', '_', 'F'))
g.let(g.term('inst', 'I')).iff(g.term('inst_mem', 'I', '_'))

# 1 { s(H,I): host(H) } 1 :- inst(I).
g.let(g.choice(1, 1, g.term('s', 'H', 'I'), g.term('host', 'H')),
      g.term('inst', 'I'))

# 0 #sum { USED,s: s(H,I): inst_mem(I,USED) } FREE :- host_mem(H, FREE).
g.sum(0, '<=', '<=', 'FREE', 'USED,s'

% Stack by trying to keep high numbered hosts empty.
#minimize { U@O: s(H,I), inst_mem(I, U), host_ord(H,O) }.

% Affinities
s(H,IA) :- s(H,IB), affinity(IA,IB).
not s(H,IA) :- host(H), s(H,IB), antiaffinity(IA,IB).
s(H,I) :- inst_cap(I,C), host_cap(H,C).

#show s/2.




<program> ::= [<statements>] [<query>]
<query> ::= <classical_literal> QUERY_MARK
<statement> ::= CONS [<body>] DOT
    | WCONS [<body>] DOT
    | <head> [CONS [<body>]] DOT
SQUARE_OPEN <weight_at_level> SQUARE_CLOSE
    | <optimize> DOT
<head> ::= <disjunction> | <choice>
<body> ::= [<body> COMMA] (<naf_literal> | [NAF] <aggregate>)
<disjunction> ::= [<disjunction> OR] <classical_literal>
<choice> ::= [<term> <binop>] CURLY_OPEN [<choice_elements>] CURLY_CLOSE [<binop> <term>]
<choice_elements> ::= [<choice_elements> SEMICOLON] <choice_element>
<choice_element> ::= <classical_literal> [COLON [<naf_literals>]]
<aggregate> ::= [<term> <binop>] <aggregate function> CURLY_OPEN [<aggregate_elements>] CURLY_CLOSE [<binop> <term>]
<aggregate_elements> ::= [<aggregate_elements> SEMICOLON] <aggregate_element>
<aggregate_element> ::= [<terms>] [COLON [<naf_literals>]]
<aggregate_function> ::= AGGREGATE_COUNT | AGGREGATE_MAX | AGGREGATE_MIN | AGGREGATE_SUM
<optimize> ::= <optimize_function> CURLY_OPEN [<optimize_elements>] CURLY_CLOSE
<optimize_function> ::= MAXIMIZE | MINIMIZE
<optimize_elements> ::= [<optimize_elements> SEMICOLON] <optimize_element>
<optimize_element> ::= <weight_at_level> [COLON [<naf_literals>]]
<weight_at_level> ::= <term> [AT <term>] [COMMA <terms>]

<naf_literals> ::= [<naf_literals> COMMA] <naf_literal>
<naf_literal> ::= [NAF] <classical_literal> | <term>
<classical_literal> ::= [MINUS] ID [PAREN_OPEN [<terms>] PAREN_CLOSE]

<terms> ::= [<terms> COMMA] <term>
<term> ::= ID [PAREN_OPEN [<terms>] PAREN_CLOSE]
    | NUMBER
    | STRING
    | VARIABLE
    | ANONYMOUS_VARIABLE
    | PAREN_OPEN <term> PAREN_CLOSE
    | MINUS <term>
    | <term> <arithop> term>
<binop> ::= EQUAL | UNEQUAL | LESS | GREATER | LESS_OR_EQ | GREATER_OR_EQ
<arithop> ::= PLUS | MINUS | TIMES | DIV
