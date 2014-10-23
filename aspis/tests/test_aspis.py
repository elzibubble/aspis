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

import testtools

from aspis import aspis


class TestAspis(testtools.TestCase):
    """Tests Aspis."""

    def setUp(self):
        super(TestAspis, self).setUp()
        self.asp = aspis.Aspis()

    def test_load(self):
        self.asp.load('sched.lp4')
        self.asp.solve()
        self.assertEquals('[s(a,1), s(a,2), s(b,3)]', str(self.asp.optimum))



#g = Aspl()
#gasp.add(g.term('host', 'a', 1, 1))

#g.aggr_element(g.term('s', 'H', 'I'), g.term('host', 'H'))

#gasp.add(g.rule(g.term('s', 'H', 'IA'),
#             g.term('s', 'H', 'IB'),
#             g.term('affinity', 'IA', 'IB')))

#print ">>>> 1 { s(H,I): host(H) } 1 :- inst(I)."
##gasp.add(g.rule(
##    g.count(1, 1, [g.aggr_element([], ['s(H,I)'], ['host(H)'])]),
##    g.term('inst', 'I')))
#gasp.add(g.rule(
#    g.count(1, 1, [([], ['s(H,I)'], ['host(H)'])]),
#    g.term('inst', 'I')))

#print ">>>> 0 #sum { USED,s: s(H,I): inst_mem(I,USED) } FREE :- host_mem(H, FREE)."
#lit = g.term('s', 'H', 'I')
#cond = g.term('inst_mem', 'I', 'USED')
#gasp.add(g.rule(
#    g.sum(0, 'FREE', [g.aggr_element(['USED', 's'], [lit], [cond])]),
#    'host_mem(H, FREE)'))

#print ">>>> #minimize { U@O: s(H,I), inst_mem(I, U), host_ord(H,O) }."
#gasp.add(g.minimize(('U', 'O',
#                     ['s(H,I)', 'inst_mem(I, U)', 'host_ord(H,O)'])))

## s(H,IA) :- s(H,IB), affinity(IA,IB).
## not s(H,IA) :- host(H), s(H,IB), antiaffinity(IA,IB).
## s(H,I) :- inst_cap(I,C), host_cap(H,C).


##info = {
##    'h1': {'total_mem': 1024},
##    'h2': {'total_mem': 1024},
##}
##for k, v in info.items():
##    for sk, sv in v.items():
##        gasp.add(g.term(g.atom('host_%s' % sk, k, sv)))
##gasp.solve()
##print gasp.optimum
