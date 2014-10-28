# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import testtools

from aspis import aspis


TEST_DIR = os.path.dirname(__file__)
Z = aspis.Aspl


class TestAspis(testtools.TestCase):
    """Tests Aspis."""

    def setUp(self):
        super(TestAspis, self).setUp()
        self.asp = aspis.Aspis()

    def tr(self, exp, act):
        self.assertEquals(exp, aspis.flatten(act))

    def solve(self, exp):
        self.asp.solve()
        self.assertEquals(exp, str(self.asp.optimum))

    def test_load(self):
        self.asp.load(os.path.join(TEST_DIR, 'sched.lp4'))
        self.solve('[s(a,1), s(a,2), s(b,3)]')

    def test_term(self):
        self.tr("host(a,1,1)", Z.term('host', 'a', 1, 1))

    def test_term_fancy(self):
        self.tr("host(a,1,1)", Z().host('a', 1, 1))

    def test_not_term_fancy(self):
        self.tr("not host(a,1,1)", Z().neg.host('a', 1, 1))

    def test_fact(self):
        self.tr("s(H,IA).",
                Z.fact(Z().s('H', 'IA')))

    def test_rule(self):
        self.tr("s(H,IA) :- s(H,IB), affinity(IA,IB).",
                Z.rule(Z().s('H', 'IA'),
                       Z().s('H', 'IB'),
                       Z().affinity('IA', 'IB')))

    def test_choice(self):
        self.tr("1 #count { s(H,I): host(H) } 1 :- inst(I).",
                Z.rule(Z.count(1, 1,
                               [Z.aggr_element([], ['s(H,I)'], ['host(H)'])]),
                       Z().inst('I')))

    def test_choice_tuple(self):
        self.tr("1 #count { s(H,I): host(H) } 1 :- inst(I).",
                Z.rule(Z.count(1, 1, [([], ['s(H,I)'], ['host(H)'])]),
                       Z.term('inst', 'I')))

    def test_aggr(self):
        self.tr("0 #sum { USED,s: s(H,I): inst_mem(I,USED) } FREE"
                + " :- host_mem(H, FREE).",
                Z.rule(Z.sum(0, 'FREE', [(['USED', 's'],
                                          [Z().s('H', 'I')],
                                          [Z().inst_mem('I', 'USED')])]),
                       'host_mem(H, FREE)'))

    def test_minimize(self):
        self.tr("#minimize { U@O: s(H,I), inst_mem(I, U), host_ord(H,O) }.",
                Z.minimize(('U', 'O',
                            ['s(H,I)', 'inst_mem(I, U)', 'host_ord(H,O)'])))

    def test_maximize(self):
        self.tr("#maximize { U@O: s(H,I) }.",
                Z.maximize(('U', 'O', ['s(H,I)'])))

    def test_dyn_facts(self):
        info = {
            'h1': {'mem': 1},
            'h2': {'mem': 2},
        }
        for k, v in info.items():
            for sk, sv in v.items():
                self.asp.add(Z.term('host_%s' % sk, k, sv))
        self.asp.add(Z.rule(Z().p('H'),
                            Z().host_mem('H', 1)))
        self.asp.add(Z.show('p', 1))
        self.solve('[p(h1)]')
