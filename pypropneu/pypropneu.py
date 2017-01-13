#!/usr/bin/python
# or:
# !C:\Python27\python.exe

# By Giovanni Sileno

import copy
import logging

logging.basicConfig(filename='pypropneu.log', filemode='w', level=logging.INFO)

class Node:
    # Fields:
    # id
    # inputs : Arc list
    # outputs : Arc list
    def __init__(self):
        self.inputs = []
        self.outputs = []

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
    # weight : Integer
    def __init__(self, source, target, type, weight):
        self.source = source
        self.target = target
        self.type = type
        self.weight = weight
        source.outputs.append(self)
        target.inputs.append(self)

class Place(Node):
    # -- Fields --
    # name : String
    # marking : Token list
    def __init__(self, name, marking):
        Node.__init__(self)
        self.name = name
        self.marking = marking

    def Flush(self):
        logging.info("Flushing " + self.name)
        self.marking = []

class TransitionEvent():
    # -- Fields --
    # transition : Transition
    # token : Token
    def __init__(self, transition, token):
        self.transition = transition
        self.token = token

class Binding(Node):
    # -- Fields --
    # name : String
    # operator : Operator
    def __init__(self, name, operator):
        Node.__init__(self)
        self.name = name
        self.operator = operator

class Transition(Node):
    # -- Fields --
    # name : String
    # operation : Operation
    def __init__(self, name, operation):
        Node.__init__(self)
        self.name = name
        self.operation = operation

    def IsEnabled(self):
        logging.info("checking transition " + self.name + " if enabled.")

        if len(self.inputs) == 0:
            logging.info("no inputs: disabled.")
            return False

        for input in self.inputs:
            if input.type == ArcType.NORMAL:
                if len(input.source.marking) < input.weight:
                    logging.info("not sufficient tokens in place " + input.source.name + ": disabled.")
                    return False
            elif input.type == ArcType.INHIBITOR:
                if len(input.source.marking) >= input.weight:
                    logging.info("threshold number of tokens reached in place " + input.source.name + ": inhibited.")
                    return False
        return True

    def Fire(self):
        logging.info("transition " + self.name + " fires..")
        print self.name + " fires"
        self.ConsumeInputTokens()
        return self.ProduceOutputTokens()

    def ConsumeInputTokens(self):
        for input in self.inputs:
            if input.type == ArcType.NORMAL:
                logging.info("consuming " + str(input.weight) + " tokens in place " + input.target.name)
                for i in range (0, input.weight):
                    input.source.marking.pop()
            else:
                raise ValueError("Unexpected type of input arc")

    def ProduceOutputTokens(self):
        token = Token()
        events = []
        for output in self.outputs:
            if output.type == ArcType.NORMAL:
                logging.info("producing " + str(output.weight) + " tokens in place " + output.target.name)
                for i in range (0, output.weight):
                    clonedToken = copy.deepcopy(token)
                    event = TransitionEvent(self, token)
                    output.target.marking.append(clonedToken)
                    events.append(event)
            elif output.type == ArcType.RESET:
                logging.info("resetting place " + output.target.name)
                output.target.Flush()
            else:
                raise ValueError("Unexpected type of input arc")
        return events

class PetriNetStructure:
    # -- Fields --
    # places : Place list
    # transitions : Transition list
    # arcs : Arc list

    def __init__(self, places, transitions, arcs):
        self.places = places
        self.transitions = transitions
        self.arcs = arcs

    def PrintMarking(self):
        output = ""
        for place in self.places:
            output = output + place.name + ": " + str(len(place.marking)) + ", "
        print output[:-2]

class PetriNet(PetriNetStructure):

    def RunSimulation(self, iterations):
        n = 0
        for i in range(iterations):
            logging.info("attempting to run step " + str(i))
            if not self.RunStep():
                break
            else:
                n = n + 1
                self.PrintMarking()
                logging.info("step " + str(i) + " completed")

        print str(n) + " steps completed."

    def RunStep(self):
        firedTransitionEvents = self.BruteForceExecution()
        return len(firedTransitionEvents) > 0

    def BruteForceExecution(self):
        firedTransition = None

        for t in self.transitions:
            if t.IsEnabled():
                t.ConsumeInputTokens()
                firedTransition = t
                break

        if firedTransition is not None:
            events = firedTransition.ProduceOutputTokens()
            print firedTransition.name + " fires"
            ## TODO: for now I implement a FIFO mechanism
            self.transitions.remove(firedTransition)
            self.transitions.append(firedTransition)
            return events
        else:
            return []

# really simple Petri net
# two places, a transition

p1 = Place("p1", "p1", [Token(), Token(), Token()])
p2 = Place("p2", "p2", [])
t1 = Transition("t1", "t1")
a1 = Arc("a1", p1, t1, ArcType.NORMAL, 1)
a2 = Arc("a2", t1, p2, ArcType.NORMAL, 1)
net = PetriNet([p1, p2], [t1], [a1, a2])

net.RunSimulation(5)