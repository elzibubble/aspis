#!/usr/bin/env python

import gringo


def flatten(l):
    if not isinstance(l, (list, tuple)):
        return str(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], (list, tuple)):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ''.join(str(i) for i in l)


def join(items, delims=None, delim='', start='', end='', allow_empty=False):
    if len(items) == 0 and not allow_empty:
        return ""
    if delims is not None:
        if len(delims) == 4:
            (start, delim, end) = (delims[0], delims[1:2], delims[3])
        elif len(delims) == 3:
            (start, delim, end) = (delims[0], delims[1], delims[2])
        else:
            delim = delims
    items = (flatten(i) for i in items if i is not None and i is not '')
    return [start, delim.join(items), end]


class Aspis(object):
    def __init__(self):
        self.c = gringo.Control()
        self.models = []
        self.assumptions = []

    def load(self, filename):
        self.c.load(filename)

    def solve(self):
        self.c.ground([('base', [])])
        with self.c.solve_iter(assumptions=self.assumptions) as it:
            for m in it:
                self.models.append((m.atoms(), m.optimization()))

        self.optimum = None
        for (atoms, opt) in self.models:
            if opt == self.c.stats['costs']:
                self.optimum = atoms

    def assume_raw(self, *assumptions):
        self.assumptions.extend(assumptions)

    def clear_assumptions(self):
        self.assumptions = []

    def add(self, *code):
        code = flatten(code)
        if not code.endswith('.'):
            code += '.'
        print "add: %s" % code
        self.c.add('base', [], code)


class Aspl(object):
    @staticmethod
    def show(atom, arity):
        return ["#show ", atom, "/", arity, "."]

    @staticmethod
    def term(name, *args):
        if len(args) == 0:
            return name
        return [name, join(args, '(, )')]

    @staticmethod
    def rule(lhs, *conds):
        return [lhs, ' :- ', join(conds, ', '), '.']

    @staticmethod
    def count(lb, ub, elements, lop='', uop=''):
        return Aspl.aggr('#count', lb, ub, elements, lop='', uop='')

    @staticmethod
    def sum(lb, ub, elements, lop='', uop=''):
        return Aspl.aggr('#sum', lb, ub, elements, lop='', uop='')

    @staticmethod
    def aggr(aop, lb, ub, elements, lop='', uop=''):
        elements = [Aspl.aggr_element(*e) if type(e) == tuple else e
                    for e in elements]
        return join([lb, lop, aop,
                     join(elements, "; ", start="{ ", end=" }"),
                     uop, ub], ' ')

    @staticmethod
    def aggr_element(terms, lits=[], conds=[]):
        terms = join(terms, ",")
        lits = join(lits, ", ", start=": ")
        conds = join(conds, ", ", start=": ")
        return [terms, lits, conds]

    @staticmethod
    def minimize(*elements):
        return Aspl.optimise('#minimize', elements)

    @staticmethod
    def optimise(oop, elements):
        elements = [Aspis.opt_element(*e) if type(e) == tuple else e
                    for e in elements]
        return join([oop, join(elements, "; ", start="{ ", end=" }")], ' ')

    @staticmethod
    def opt_element(weight, priority=0, lits=[]):
        wap = join([weight,priority], "@")
        lits = join(lits, ", ", start=": ")
        return [wap, lits]
