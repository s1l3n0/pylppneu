import unittest
from pypneu import Place, Transition, Arc, PetriNetExecution, ArcType, PetriNetAnalysis

class PyPneuTestCase(unittest.TestCase):

    # really simple Petri net
    # two places, one transition
    def test_simulation_1(self):
        p1 = Place("p1", 3)
        p2 = Place("p2", 0)
        t1 = Transition("t1")
        a1 = Arc(p1, t1, ArcType.NORMAL, 1)
        a2 = Arc(t1, p2, ArcType.NORMAL, 1)
        net = PetriNetExecution([p1, p2], [t1], [a1, a2])
        assert net.run_simulation(5) == 3

    def test_analysis_1(self):
        p1 = Place("p1", 3)
        p2 = Place("p2", 0)
        t1 = Transition("t1")
        a1 = Arc(p1, t1, ArcType.NORMAL, 1)
        a2 = Arc(t1, p2, ArcType.NORMAL, 1)
        net = PetriNetAnalysis([p1, p2], [t1], [a1, a2])
        assert net.run_analysis(5) == 3
        assert len(net.state_base) == 4
        assert len(net.path_base) == 1

    # simple Petri net with fork
    # one place, two transition
    def test_simulation_2(self):
        p1 = Place("p1", 3)
        t1 = Transition("t1")
        t2 = Transition("t2")
        a1 = Arc(p1, t1)
        a2 = Arc(p1, t2)
        net = PetriNetExecution([p1], [t1, t2], [a1, a2])
        assert net.run_simulation(10) == 3

    def test_analysis_2(self):
        p1 = Place("p1", 3)
        t1 = Transition("t1")
        t2 = Transition("t2")
        a1 = Arc(p1, t1)
        a2 = Arc(p1, t2)
        net = PetriNetAnalysis([p1], [t1, t2], [a1, a2])

        assert net.run_analysis(10) == 6
        assert len(net.state_base) == 4
        assert len(net.path_base) == 4


if __name__ == '__main__':
    unittest.main()