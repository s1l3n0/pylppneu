#!/usr/bin/python
# or:
# !C:\Python27\python.exe

# By Giovanni Sileno

import copy
import logging

logging.basicConfig(filename='pypneu.log', filemode='w', level=logging.INFO)


class Node:
    # Fields:
    # inputs
    # outputs
    def __init__(self):
        self.inputs = []
        self.outputs = []

class ArcType:
    NORMAL = 1
    INHIBITOR = 2
    RESET = 3


class Arc:
    # Fields:
    # source
    # target
    # arc type
    # weight
    def __init__(self, source, target, type, weight):
        self.source = source
        self.target = target
        self.type = type
        self.weight = weight
        source.outputs.append(self)
        target.inputs.append(self)


class Place(Node):
    # Fields:
    # name
    # marking
    def __init__(self, name = None, marking = 0):
        Node.__init__(self)
        self.name = name
        self.marking = marking

    def Flush(self):
        logging.info("Flushing " + self.name)
        self.marking = 0


class TransitionEvent():
    # Fields:
    # transition
    def __init__(self, transition):
        self.transition = transition


class Transition(Node):
    # Fields:
    # name
    def __init__(self, name = None):
        Node.__init__(self)
        self.name = name

    def IsEnabled(self):
        logging.info("checking transition " + self.name + " if enabled.")

        if len(self.inputs) == 0:
            logging.info("no inputs: disabled.")
            return False

        for input in self.inputs:
            if input.type == ArcType.NORMAL:
                if input.source.marking < input.weight:
                    logging.info("not sufficient tokens in place " + input.source.name + ": disabled.")
                    return False
            elif input.type == ArcType.INHIBITOR:
                if input.source.marking >= input.weight:
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
                logging.info("consuming " + str(input.weight) + " tokens in place " + input.source.name)
                input.source.marking -= input.weight
            else:
                raise ValueError("Unexpected type of input arc")

    def ProduceOutputTokens(self):
        events = []
        for output in self.outputs:
            if output.type == ArcType.NORMAL:
                logging.info("producing " + str(output.weight) + " tokens in place " + output.target.name)
                for i in range (0, output.weight):
                    event = TransitionEvent(self)
                    output.target.marking += 1
                    events.append(event)
            elif output.type == ArcType.RESET:
                logging.info("resetting place " + output.target.name)
                output.target.Flush()
            else:
                raise ValueError("Unexpected type of input arc")
        return events


class PetriNetStructure:
    # Fields:
    # places
    # transitions
    # arcs

    def __init__(self, places, transitions, arcs):
        self.places = places
        self.transitions = transitions
        self.arcs = arcs

    def PrintMarking(self):
        output = ""
        for place in self.places:
            output = output + place.name + ": " + str(place.marking) + ", "
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
                ## to have a rotation, I simply implement a FIFO mechanism
                self.transitions.remove(firedTransition)
                self.transitions.append(firedTransition)
                break

        if firedTransition is not None:
            print firedTransition.name + " fires"
            events = firedTransition.ProduceOutputTokens()
            return events
        else:
            return []

# really simple Petri net
# two places, a transition

p1 = Place("p1", 3)
p2 = Place("p2", 0)
t1 = Transition("t1")
a1 = Arc(p1, t1, ArcType.NORMAL, 1)
a2 = Arc(t1, p2, ArcType.NORMAL, 1)
net = PetriNet([p1, p2], [t1], [a1, a2])

net.RunSimulation(5)