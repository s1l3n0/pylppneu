from pypropneu import Place, Transition, Arc, PetriNetExecution, Binding, BindingOperator, PetriNetAnalysis
from pyecpropneu import PetriNetEventCalculus

def buildSerial(p1, p2):
    t1 = Transition()
    a1 = Arc(p1, t1)
    a2 = Arc(t1, p2)
    return (t1, (a1, a2))

def buildFork(p1, t1, t2):
    a1 = Arc(p1, t1)
    a2 = Arc(p1, t2)
    return (a1, a2)

def buildJoin(t1, t2, p1):
    p1 = Place()
    t1 = Transition()
    t2 = Transition()
    a1 = Arc(t1, p1)
    a2 = Arc(t2, p1)
    return (a1, a2)

def buildBinding(n1, n2, n3, operator):
    b1 = Binding(operator)
    a1 = Arc(n1, b1)
    a2 = Arc(n2, b1)
    a3 = Arc(b1, n3)
    return ((a1, a2, a3), (b1))

def buildAndBinding(n1, n2, n3):
    return buildBinding(n1, n2, n3, BindingOperator.AND)

def buildOrBinding(n1, n2, n3):
    return buildBinding(n1, n2, n3, BindingOperator.OR)

def buildImpliesBinding(n1, n2, n3):
    return buildBinding(n1, n2, n3, BindingOperator.IMPLIES)

def buildEquivalenceBinding(n1, n2, n3):
    return buildBinding(n1, n2, n3, BindingOperator.EQUIV)

places = []
transitions = []
arcs = []
p_bindings = []
t_bindings = []

p1 = Place(marking=True)
for i in range(1, 2):
    p2 = Place()
    places.extend([p1, p2])
    (t1, (a1, a2)) = buildSerial(p1, p2)
    transitions.append(t1)
    arcs.extend([a1, a2])
    p1 = p2

# net = PetriNetAnalysis(places, transitions, arcs)
#
# net.run_analysis(200)

netEC = PetriNetEventCalculus(places, transitions, arcs)

print netEC.build_event_calculus_program()