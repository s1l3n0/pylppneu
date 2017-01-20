#!/usr/bin/python
# or:
# !C:\Python27\python.exe

# By Giovanni Sileno

import logging
from clingo import Control, Function, parse_program

logging.basicConfig(filename='pypropneu.log', filemode='w', level=logging.INFO)


class Node:
    # Fields:
    # id
    # inputs : Arc list
    # outputs : Arc list
    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.nid = None              ## assigned when attached to a net

class Token:
    # Fields:
    # label : String
    def __init__(self, label=None):
        self.label = label


class ArcType:
    NORMAL = 1
    INHIBITOR = 2
    RESET = 3


class Arc:
    # -- Fields --
    # id
    # source : Node
    # target : Node
    # arc type : NORMAL, INHIBITOR or RESET
    def __init__(self, source, target, type=ArcType.NORMAL):
        self.source = source
        self.target = target
        self.type = type
        source.outputs.append(self)
        target.inputs.append(self)


class Place(Node):
    # -- Fields --
    # name : String
    # marking : Token list
    def __init__(self, name, marking=False):
        Node.__init__(self)
        self.name = name
        self.marking = marking

    def Flush(self):
        logging.info("Flushing " + self.name)
        self.marking = False


class BindingOperator():
    NOT = 0
    AND = 1
    OR = 2
    XOR = 3
    IMPLIES = 4
    EQUIV = 5


class Binding(Node):

    # -- Fields --
    # name : String
    # operator : Operator
    def __init__(self, operator):
        Node.__init__(self)
        self.operator = operator

    def to_ASP(self):
        code = ""
        if self.operator is BindingOperator.AND:
            if len(self.outputs) != 1:
                raise ValueError("Wrong binding constraint")

            code += self.outputs[0].target.nid + " :- "
            for input in self.inputs:
                code += input.source.nid + ", "
            code = code[:-2]+"."
        elif self.operator is BindingOperator.OR:
            raise ValueError("Not yet implemented")
        elif self.operator is BindingOperator.XOR:
            raise ValueError("Not yet implemented")
        elif self.operator is BindingOperator.IMPLIES:
            if len(self.outputs) != 1:
                raise ValueError("Wrong binding constraint")
            code += self.outputs[0].target.nid + " :- "
            for input in self.inputs:
                code += input.source.nid + ", "
            code = code[:-2]+"."
        elif self.operator is BindingOperator.EQUIV:
            raise ValueError("Not yet implemented")
        return code


class Transition(Node):

    # -- Fields --
    # name : String
    def __init__(self, name):
        Node.__init__(self)
        self.name = name

    def IsEnabled(self):
        logging.info("checking transition " + self.name + " if enabled.")

        if len(self.inputs) == 0:
            logging.info("no inputs: disabled.")
            return False

        found = False
        for input in self.inputs:
            if input.type == ArcType.NORMAL:
                if input.source.__class__ is Place:
                    if input.source.marking is False:
                        logging.info("no token is available in place " + input.source.name + ": disabled.")
                        return False
                    else: found = True
            elif input.type == ArcType.INHIBITOR:
                if input.source.__class__ is Place:
                    if input.source.marking is True:
                        logging.info("token in place " + input.source.name + ": inhibited.")
                        return False
                    else: found = True

        if found: return True
        else: return False

    def ConsumeInputTokens(self):
        for input in self.inputs:
            if input.type == ArcType.NORMAL:
                if input.source.__class__ is Place:
                    if input.source.marking is False:
                        raise ValueError("There should be a token in place "+input.source.name)
                    logging.info("consuming token in place " + input.source.name)
                    input.source.marking = False
            else:
                raise ValueError("Unexpected type of input arc")

    def ProduceOutputTokens(self):
        token = Token()
        events = []
        for output in self.outputs:
            if output.type == ArcType.NORMAL:
                if output.target.__class__ is Place:
                    logging.info("producing token in place " + output.target.name)
                    event = TransitionEvent(self, token)
                    output.target.marking = True
                    events.append(event)
            elif output.type == ArcType.RESET:
                if output.target.__class__ is Place:
                    logging.info("resetting place " + output.target.name)
                    output.target.Flush()
            else:
                raise ValueError("Unexpected type of input arc")
        return events


class TransitionEvent():
    # -- Fields --
    # transition : Transition
    # token : Token
    def __init__(self, transition, token):
        self.transition = transition
        self.token = token


class PetriNetStructure:
    # -- Fields --
    # places : Place list
    # transitions : Transition list
    # arcs : Arc list

    def __build_dict(self, nodes):
        dict = {}
        for node in nodes:
            nid = node.name
            if dict.has_key(nid):
                i = 1
                while dict.has_key(nid):
                    i += 1
                    nid = node.name + "_" + str(i)
            dict[nid] = node
            node.nid = nid
        return dict

    def __init__(self, places=(), transitions=(), p_bindings=(), t_bindings=(), arcs=()):
        self.places = places
        self.id2place = self.__build_dict(places)
        self.transitions = transitions
        self.id2transition = self.__build_dict(transitions)
        self.p_bindings = p_bindings
        self.t_bindings = t_bindings
        self.arcs = arcs

    def PrintMarking(self):
        output = ""
        for place in self.places:
            output = output + place.name + ": " + str(place.marking) + ", "
        print output[:-2]

    def __bindings_code(self, bindings):
        code = ""
        for binding in bindings:
            code += binding.to_ASP()
        return code

    def p_bindings_code(self):
        return self.__bindings_code(self.p_bindings)

    def t_bindings_code(self):
        return self.__bindings_code(self.t_bindings)

    def __interface_code(self, nodes):
        code = ""
        for node in nodes:
            code += "#external " + node.nid + ".\n"
        return code

    def p_interface_code(self):
        return self.__interface_code(self.places)

    def t_interface_code(self):
        return self.__interface_code(self.transitions)

    def p_code(self):
        return self.p_interface_code() + self.p_bindings_code()

    def t_code(self):
        return self.t_interface_code() + self.t_bindings_code()


class PetriNet(PetriNetStructure):

    def update_pid(self, model):
        for atom in model.symbols(shown=True):
            logging.info("updating " + str(atom) + " to true")
            self.id2place[str(atom)].marking = True

    def update_tid(self, model):
        for atom in model.symbols(shown=True):
            logging.info("adding " + str(atom) + " to transition to be fired")
            self.transitions_to_be_fired.append(self.id2transition[str(atom)])

    def RunSimulation(self, iterations):

        out_file = open("../tmp/p.lp", "w")
        out_file.write(self.p_code())
        out_file.close()

        ## create the ASP solver control for the constraints on places
        p_prog = Control()
        p_prog.configuration.solve.models = 0  # to obtain all answer sets
        # logging.info("ASP program binding places: "+ self.p_code())
        with p_prog.builder() as builder:
            parse_program(self.p_code(), lambda statement: builder.add(statement))
        p_prog.ground([("base", [])])

        out_file = open("../tmp/t.lp", "w")
        out_file.write(self.t_code())
        out_file.close()

        ## create the ASP solver control for the constraints on transitions
        t_prog = Control()
        t_prog.configuration.solve.models = 0
        # logging.info("ASP program binding transitions: " + self.t_code())
        with t_prog.builder() as builder:
            parse_program(self.t_code(), lambda statement: builder.add(statement))
        t_prog.ground([("base", [])])

        n = 0
        self.PrintMarking()

        for i in range(iterations):

            self.transitions_to_be_fired = []

            logging.info("resolution bindings on places")
            logging.info("assign current marking")
            ## assign current marking
            for place in self.places:
                if place.marking is True:
                    logging.info("assigning " + place.nid + " to true")
                    p_prog.assign_external(Function(place.nid), True)
                else:
                    logging.info("assigning " + place.nid + " to false")
                    p_prog.assign_external(Function(place.nid), False)

            logging.info("solving bindings on places...")
            ## solve and update marking [TODO: check only one answer sets!]
            p_prog.solve(on_model=self.update_pid)

            logging.info("attempting to run step " + str(i))
            if not self.RunStep(t_prog):
                break
            else:
                n = n + 1
                logging.info("step " + str(i) + " completed")

        self.PrintMarking()

        print str(n) + " steps completed."

    def RunStep(self, t_prog):
        firedTransitionEvents = self.BruteForceExecution(t_prog)
        return len(firedTransitionEvents) > 0

    def BruteForceExecution(self, t_prog):
        preFiredTransition = None

        logging.info("looking for enabled transitions...")
        for t in self.transitions:
            if t.IsEnabled():
                logging.info("pre-fire " + t.name + "!!!")
                preFiredTransition = t
                ## to have a rotation, I simply implement a FIFO mechanism
                self.transitions.remove(preFiredTransition)
                self.transitions.append(preFiredTransition)
                break

        if preFiredTransition is not None:
            print preFiredTransition.name + " pre-fires"

            logging.info("resolution bindings on transitions...")

            logging.info("assign current pre-fire")
            for transition in self.transitions:
                if transition == preFiredTransition:
                    logging.info("assigning " + transition.nid + " to true")
                    t_prog.assign_external(Function(transition.nid), True)
                else:
                    logging.info("assigning " + transition.nid + " to false")
                    t_prog.assign_external(Function(transition.nid), False)

            ## solve and get transition events [TODO: check only one answer sets!]
            t_prog.solve(on_model=self.update_tid)

            events = []
            for firedTransition in self.transitions_to_be_fired:
                print firedTransition.name + " fires"
                firedTransition.ConsumeInputTokens()
                events.extend(firedTransition.ProduceOutputTokens())
            return events
        else:
            return []

# really simple Petri net
# two places, a transition, a logic operator on places and one on transitions

p1 = Place("p1", True)
p2 = Place("p2", False)
p3 = Place("p3", False)
p4 = Place("p4", False)
p5 = Place("p5", False)

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

net = PetriNet([p1, p2, p3, p4, p5], [t1, t2], [bp1], [bt1], [a1, a2, a3, a4, a5, a6, a7, a8])

net.RunSimulation(5)
