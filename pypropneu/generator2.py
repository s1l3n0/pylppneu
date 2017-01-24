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

def buildSerialPetriNet(n=1):
    places = []
    transitions = []
    arcs = []

    p1 = Place(marking=True)
    places.append(p1)
    for i in range(1, n+1):
        p2 = Place()
        places.append(p2)
        (t1, (a1, a2)) = buildSerial(p1, p2)
        transitions.append(t1)
        arcs.extend([a1, a2])
        p1 = p2

    return places, transitions, arcs

def buildForkPetriNet(depth=1, outputs=2, p_input=None):
    places = []
    transitions = []
    arcs = []

    if p_input is None:
        p_input = Place(marking=True)
    places.append(p_input)

    for i in range(1, outputs+1):
        t = Transition()
        transitions.append(t)
        a1 = Arc(p_input, t)
        p_output = Place()
        a2 = Arc(t, p_output)
        arcs.extend([a1, a2])

        if depth > 1:
            (inner_places, inner_transitions, inner_arcs) = buildForkPetriNet(depth - 1, outputs, p_output)
        else:
            (inner_places, inner_transitions, inner_arcs) = ([p_output], [], [])

        places.extend(inner_places)
        if len(inner_transitions) > 0: transitions.extend(inner_transitions)
        if len(inner_arcs) > 0: arcs.extend(inner_arcs)

    return places, transitions, arcs

evaluation_file = open("../tmp/evaluation.txt", "w")

for i in range(1, 11, 1):
    for n in 1, 2, 4, 8:
        (places, transitions, arcs) = buildSerialPetriNet(n)
        net = PetriNetAnalysis(places, transitions, arcs)
        (models, timing, iterations) = net.run_analysis()
        evaluation_file.write(str(i) + ";" + str(n) + ";" + "1s" + ";" + "LPPN" + ";" + str(models) + ";" + str(timing) + "\n")

        (places, transitions, arcs) = buildSerialPetriNet(n)
        netEC = PetriNetEventCalculus(places, transitions, arcs)
        (models, timing) = netEC.solve(n-1)
        evaluation_file.write(str(i) + ";" + str(n) + ";" + "1s" + ";" + "EC" + ";" + str(models) + ";" + str(timing) + "\n")

        for d in 1, 2, 3:
            (places, transitions, arcs) = buildForkPetriNet(n, d)
            net = PetriNetAnalysis(places, transitions, arcs)
            (models, timing, iterations) = net.run_analysis(bug=True)
            evaluation_file.write(
                str(i) + ";" + str(n) + ";" + str(d) + ";" + "LPPN" + ";" + str(models) + ";" + str(timing) + "\n")

            (places, transitions, arcs) = buildForkPetriNet(n, d)
            netEC = PetriNetEventCalculus(places, transitions, arcs)
            (models, timing) = netEC.solve(n)
            evaluation_file.write(str(i) + ";" + str(n) + ";" + str(d) + ";" + "EC" + ";" + str(models) + ";" + str(timing) + "\n")

evaluation_file.close()
