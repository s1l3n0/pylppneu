import unittest
from pypropneu import Place, Transition, Arc, PetriNetExecution, Binding, BindingOperator, PetriNetAnalysis

class PyProPneuTestCase(unittest.TestCase):

    # really simple Petri net
    # two places, one transition
    def test_simulation_1(self):
        p1 = Place("p1", True)
        p2 = Place("p2")
        t1 = Transition("t1")
        a1 = Arc(p1, t1)
        a2 = Arc(t1, p2)
        net = PetriNetExecution(places=[p1, p2], transitions=[t1], arcs=[a1, a2])
        assert net.run_simulation(5) == 1

    def test_analysis_1(self):
        p1 = Place("p1", True)
        p2 = Place("p2")
        p3 = Place("p3")

        t1 = Transition("t1")
        t2 = Transition("t2")
        a1 = Arc(p1, t1)
        a2 = Arc(t1, p2)
        a3 = Arc(p2, t2)
        a4 = Arc(t2, p3)

        net = PetriNetAnalysis(places=[p1, p2, p3], transitions=[t1, t2], arcs=[a1, a2, a3, a4])
        assert net.run_analysis()[2] == 2
        assert len(net.path_base) == 1

    # simple Petri net with fork
    # one place, two transition
    def test_simulation_2(self):
        p1 = Place("p1", True)
        t1 = Transition("t1")
        t2 = Transition("t2")
        a1 = Arc(p1, t1)
        a2 = Arc(p1, t2)
        net = PetriNetExecution(places=[p1], transitions=[t1, t2], arcs=[a1, a2])
        assert net.run_simulation(10) == 1

    def test_analysis_2(self):
        p1 = Place("p1", True)
        t1 = Transition("t1")
        t2 = Transition("t2")
        a1 = Arc(p1, t1)
        a2 = Arc(p1, t2)
        net = PetriNetAnalysis([p1], [t1, t2], [a1, a2])

        assert net.run_analysis()[2] == 2
        assert len(net.state_base) == 2
        assert len(net.path_base) == 2

    # simple Logic Programming Petri net
    # two places, a transition, a logic operator on places and one on transitions
    def test_simulation_3(self):
        p1 = Place("p1", True)
        p2 = Place("p2")
        p3 = Place("p3")
        p4 = Place("p4")
        p5 = Place("p5")

        bp1 = Binding(BindingOperator.AND)
        bt1 = Binding(BindingOperator.IMPLIES)

        t1 = Transition("t1")
        t2 = Transition("t2")

        a1 = Arc(p1, t1)
        a2 = Arc(t1, p2)

        a3 = Arc(p2, bp1)
        a4 = Arc(p5, bp1)
        a5 = Arc(bp1, p4)

        a6 = Arc(t1, bt1)
        a7 = Arc(bt1, t2)

        a8 = Arc(t2, p5)

        net = PetriNetExecution(
            places=[p1, p2, p3, p4, p5],
            transitions=[t1, t2],
            p_bindings=[bp1],
            t_bindings=[bt1],
            arcs=[a1, a2, a3, a4, a5, a6, a7, a8])

        assert p1.marking is True
        assert p2.marking is False
        assert p3.marking is False
        assert p4.marking is False
        assert p5.marking is False

        assert net.run_simulation(5) == 1

        assert p1.marking is False
        assert p2.marking is True
        assert p3.marking is False
        assert p4.marking is True  # p2 and p5 implies p4
        assert p5.marking is True  # t1 implies t2 that generates p5

    # simple Logic Programming Petri net
    # two places, a transition, a logic operator on places and one on transitions
    def test_analysis_4(self):
        p1 = Place("p1", True)
        p2 = Place("p2")
        p3 = Place("p3")
        p4 = Place("p4")
        p5 = Place("p5")

        bp1 = Binding(BindingOperator.AND)
        bt1 = Binding(BindingOperator.IMPLIES)

        t1 = Transition("t1")
        t2 = Transition("t2")

        a1 = Arc(p1, t1)
        a2 = Arc(t1, p2)

        a3 = Arc(p2, bp1)
        a4 = Arc(p5, bp1)
        a5 = Arc(bp1, p4)

        a6 = Arc(t1, bt1)
        a7 = Arc(bt1, t2)

        a8 = Arc(t2, p5)

        net = PetriNetAnalysis(
            places=[p1, p2, p3, p4, p5],
            transitions=[t1, t2],
            p_bindings=[bp1],
            t_bindings=[bt1],
            arcs=[a1, a2, a3, a4, a5, a6, a7, a8])

        assert p1.marking is True
        assert p2.marking is False
        assert p3.marking is False
        assert p4.marking is False
        assert p5.marking is False

        assert net.run_analysis()[2] == 1

        assert p1.marking is False
        assert p2.marking is True
        assert p3.marking is False
        assert p4.marking is True  # p2 and p5 implies p4
        assert p5.marking is True  # t1 implies t2 that generates p5

    # simple Logic Programming Petri net
    # two places, a transition, a logic operator on places and one on transitions
    def test_analysis_5(self):
        p1 = Place("a", None)
        p2 = Place("b", None)
        p3 = Place("c", True)

        bp1 = Binding(BindingOperator.OR)

        a1 = Arc(p1, bp1)
        a2 = Arc(p2, bp1)
        a3 = Arc(bp1, p3)

        net = PetriNetAnalysis(
            places=[p1, p2, p3],
            p_bindings=[bp1],
            arcs=[a1, a2, a3])

        assert p1.marking is None
        assert p2.marking is None
        assert p3.marking is True

        assert net.run_analysis()[2] == 0
        assert len(net.path_base) == 3
        assert len(net.state_base) == 3

if __name__ == '__main__':
    unittest.main()