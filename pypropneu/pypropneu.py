#!/usr/bin/python
# or:
# !C:\Python27\python.exe

# By Giovanni Sileno

import logging
from clingo import Control, Function, parse_program
from collections import deque
from timeit import default_timer as timer

# logging.basicConfig(filename='pypropneu.log', filemode='w', level=# logging.INFO)


class Node:
    # Fields
    # inputs : Arc list
    # outputs : Arc list
    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.nid = None ## assigned when attached to a net

    def __str__(self):
        if self.nid == None:
            return "Not attached to a net yet."
        else:
            return self.nid


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
    def __init__(self, name="p", marking=False):
        Node.__init__(self)
        self.name = name
        self.marking = marking

    def Flush(self):
        # logging.info("Flushing " + self.name)
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
            if len(self.outputs) != 1:
                raise ValueError("Wrong binding constraint")

            code += self.outputs[0].target.nid + " :- 1{"
            for input in self.inputs:
                code += input.source.nid + "; "
            code = code[:-2]+"}."
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
    def __init__(self, name="t"):
        Node.__init__(self)
        self.name = name

    def is_enabled(self):
        # logging.info("checking transition " + self.name + " if enabled.")

        if len(self.inputs) == 0:
            # logging.info("no inputs: disabled.")
            return False

        found = False
        for input in self.inputs:
            if input.type == ArcType.NORMAL:
                if input.source.__class__ is Place:
                    if input.source.marking is False:
                        # logging.info("no token is available in place " + input.source.name + ": disabled.")
                        return False
                    else: found = True
            elif input.type == ArcType.INHIBITOR:
                if input.source.__class__ is Place:
                    if input.source.marking is True:
                        # logging.info("token in place " + input.source.name + ": inhibited.")
                        return False
                    else: found = True

        if found: return True
        else: return False

    def consume_input_tokens(self):
        for input in self.inputs:
            if input.type == ArcType.NORMAL:
                if input.source.__class__ is Place:
                    if input.source.marking is False:
                        raise ValueError("There should be a token in place "+input.source.name)
                    # logging.info("consuming token in place " + input.source.name)
                    input.source.marking = False
            else:
                raise ValueError("Unexpected type of input arc")

    def produce_output_tokens(self):
        for output in self.outputs:
            if output.type == ArcType.NORMAL:
                if output.target.__class__ is Place:
                    # logging.info("producing token in place " + output.target.name)
                    output.target.marking = True
            elif output.type == ArcType.RESET:
                if output.target.__class__ is Place:
                    # logging.info("resetting place " + output.target.name)
                    output.target.flush()
            else:
                raise ValueError("Unexpected type of input arc")



class PetriNetStructure:
    # -- Fields --
    # places : Place list
    # transitions : Transition list
    # arcs : Arc list
    # p_bindings : Bindings list on places
    # t_bindings : Bindings list on transitions

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

    def __init__(self, places=(), transitions=(), arcs=(), p_bindings=(), t_bindings=()):
        self.places = places
        self.transitions = transitions
        self.arcs = arcs
        self.id2place = self.__build_dict(places)
        self.id2transition = self.__build_dict(transitions)
        self.p_bindings = p_bindings
        self.t_bindings = t_bindings

    def marking_to_string(self):
        output = ""
        for place in self.places:
            output = output + place.nid + ": " + str(place.marking) + ", "
        return output[:-2]

    @staticmethod
    def __bindings_code(bindings):
        code = ""
        for binding in bindings:
            code += binding.to_ASP()
        return code

    def p_bindings_code(self):
        return self.__bindings_code(self.p_bindings)

    def t_bindings_code(self):
        return self.__bindings_code(self.t_bindings)

    @staticmethod
    def __interface_code(nodes):
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


class PetriNetExecution(PetriNetStructure):

    def __init__(self, places=(), transitions=(), arcs=(), p_bindings=(), t_bindings=()):
        PetriNetStructure.__init__(self, places, transitions, arcs, p_bindings, t_bindings)
        self.p_prog = None
        self.t_prog = None

    def update_pid(self, model):
        for atom in model.symbols(shown=True):
            # logging.info("updating " + str(atom) + " to true")
            self.id2place[str(atom)].marking = True

    def update_tid(self, model):
        for atom in model.symbols(shown=True):
            # logging.info("adding " + str(atom) + " to transition to be fired")
            self.transitions_to_be_fired.append(self.id2transition[str(atom)])

    def init_control(self):

        p_code = self.p_code()
        out_file = open("../tmp/p.lp", "w")
        out_file.write(p_code)
        out_file.close()

        ## create the ASP solver control for the constraints on places
        self.p_prog = Control()
        self.p_prog.configuration.solve.models = 0  # to obtain all answer sets
        # # logging.info("ASP program binding places: "+ self.p_code())
        with self.p_prog.builder() as builder:
            parse_program(p_code, lambda statement: builder.add(statement))
        self.p_prog.ground([("base", [])])

        t_code = self.t_code()
        out_file = open("../tmp/t.lp", "w")
        out_file.write(t_code)
        out_file.close()

        ## create the ASP solver control for the constraints on transitions
        self.t_prog = Control()
        self.t_prog.configuration.solve.models = 0
        # # logging.info("ASP program binding transitions: " + self.t_code())
        with self.t_prog.builder() as builder:
            parse_program(t_code, lambda statement: builder.add(statement))
        self.t_prog.ground([("base", [])])

    def run_simulation(self, iterations):

        self.init_control()

        n = 0

        for i in range(iterations):
            # logging.info("attempting to run step " + str(i))
            if not self.run_execution_step():
                break
            else:
                n = n + 1
                # logging.info("step " + str(i) + " completed")

        print self.marking_to_string()

        print str(n) + " steps completed."
        return n

    def run_execution_step(self):

        self.transitions_to_be_fired = []

        # logging.info("resolution bindings on places")
        # logging.info("assign current marking")
        ## assign current marking
        for place in self.places:
            # logging.info("assigning " + place.nid + " to "+str(place.marking))
            self.p_prog.assign_external(Function(place.nid), place.marking)

        # logging.info("solving bindings on places...")
        ## solve and update marking [TODO: check only one answer sets!]
        self.p_prog.solve(on_model=self.update_pid)

        firedTransitionEvents = self.brute_force_execution()
        return len(firedTransitionEvents) > 0

    def brute_force_execution(self):
        preFiredTransition = None

        # logging.info("looking for enabled transitions...")
        for t in self.transitions:
            if t.is_enabled():
                # logging.info("pre-fire " + t.name + "!!!")
                preFiredTransition = t
                ## to have a rotation, I simply implement a FIFO mechanism
                self.transitions.remove(preFiredTransition)
                self.transitions.append(preFiredTransition)
                break

        if preFiredTransition is not None:
            # print preFiredTransition.name + " pre-fires"

            # logging.info("resolution bindings on transitions...")

            # logging.info("assign current pre-fire")
            for transition in self.transitions:
                if transition == preFiredTransition:
                    # logging.info("assigning " + transition.nid + " to true")
                    self.t_prog.assign_external(Function(transition.nid), True)
                else:
                    # logging.info("assigning " + transition.nid + " to false")
                    self.t_prog.assign_external(Function(transition.nid), False)

            ## solve and get transition events [TODO: check only one answer sets!]
            self.t_prog.solve(on_model=self.update_tid)

            events = []
            for firedTransition in self.transitions_to_be_fired:
                # print firedTransition.name + " fires"
                firedTransition.consume_input_tokens()
                events.append(firedTransition.produce_output_tokens())
            return events
        else:
            return []

    def fire(self, fired_transitions_group):
        events = []
        for fired_transition in fired_transitions_group.set:
            # print fired_transition.name + " fires"
            fired_transition.consume_input_tokens()
            events.append(fired_transition.produce_output_tokens())
        return events


class PetriNetAnalysis(PetriNetExecution):

    def __init__(self, places=(), transitions=(), arcs=(), p_bindings=(), t_bindings=()):
        PetriNetStructure.__init__(self, places, transitions, arcs, p_bindings, t_bindings)
        self.path_base = None
        self.state_base = None
        self.current_path = None
        self.current_state = None
        self.base_path = None
        self.base_state = None
        self.last_events = None
        self.markings = None
        self.fireable_groups = None
        self.restarted = None

    def status(self):
        # print "Summary: " + self.pathBase.toLog()
        print "######################## "
        if self.path_base is not None:
            print "paths: "
            for path in self.path_base:
                print str(path)
        if self.state_base is not None:
            print "states: "
            for state in self.state_base:
                print str(state)
        print "######################## "

    def update_pid(self, model):
        for atom in model.symbols(shown=True):
            self.id2place[str(atom)].marking = True
        self.current_path = self.base_path.clone()
        self.current_state = self.save_consequent(self.base_state, self.last_events)
        # logging.info("received new place model: "+str(self.current_state))
        # record the starting path
        if self.current_state not in self.markings:
            # logging.info("record the starting path...")
            self.markings.append(self.current_state)
            self.path_base.append(self.current_path)

    def update_tid(self, model):
        fireable_group = []
        for atom in model.symbols(shown=True):
            # logging.info("adding " + str(atom) + " to transition to be fired")
            fireable_group.append(self.id2transition[str(atom)])
        self.fireable_groups.append(Group(fireable_group))
        # logging.info("received new transition model: "+str(fireable_group))

    def get_fireable_groups(self, fireable_transition):
        # logging.info("resolution bindings on transitions...")
        # logging.info("assign current pre-fire")
        for transition in self.transitions:
            if transition == fireable_transition:
                # logging.info("assigning " + transition.nid + " to true")
                self.t_prog.assign_external(Function(transition.nid), True)
            else:
                # logging.info("assigning " + transition.nid + " to false")
                self.t_prog.assign_external(Function(transition.nid), False)
        self.fireable_groups = []
        self.t_prog.solve(on_model=self.update_tid)

    def run_analysis(self, iterations = 2000, bug=False):

        self.init_control()
        self.path_base = deque()
        self.state_base = deque()
        self.current_path = None
        self.current_state = None
        self.base_path = Path()
        self.base_state = None
        self.last_events = ()
        self.bug = bug ## TODO: nasty bug in counting paths for forks.

        start = timer()
        n = 0
        for i in range(iterations):
            # logging.info("attempting to run analysis step " + str(i))
            if self.run_analysis_step() is False:
                break
            else:
                n = n + 1
                # logging.info("step " + str(i) + " completed")
        end = timer()

        timing = end - start
        print str(len(self.path_base)) + " paths found (" + str(n) + " iterations) in " + str(timing) + " ms."

        # self.status()
        return len(self.path_base), timing, n

    # save the current marking, if it was not already saved before
    def save_state(self):
        marking = {}
        for place in self.places:
            marking[place.nid] = place.marking
        for state in self.state_base:
            if state.marking == marking:
                return state

        new_state = State(marking=marking, sid="s"+str(len(self.state_base)))
        # logging.info("creating state "+str(new_state))

        all_fireable_groups = []
        self.fireable_groups = []
        if new_state.events_to_state is None:
            for transition in self.transitions:
                if transition.is_enabled():
                    self.get_fireable_groups(transition)
                    for group in self.fireable_groups:
                        if group not in all_fireable_groups:
                            all_fireable_groups.append(group)

            new_state.events_to_state = {}
            for group in all_fireable_groups:
                new_state.events_to_state[group] = None
                # logging.info("attaching group of events to "+str(new_state))

        self.state_base.append(new_state)
        return new_state

    # save the current state as consequent of a given firing
    def save_consequent(self, antecedent = None, fired_events = ()):
        state = self.save_state()
        # logging.info("anchoring state "+state.sid+" to current path")
        self.current_path.steps.append(state)
        if len(fired_events) > 0:
            # logging.info("saving connection " + antecedent.sid + " -->|" + str(fired_events) + "|-->" + state.sid)
            if fired_events in antecedent.events_to_state:
                antecedent.events_to_state[fired_events] = state
                self.current_path.events_per_steps.append(fired_events)
            else:
                raise ValueError("I expected to have these events already saved in the antecedent.")
        return state

    def load_state(self, state):
        # logging.info("recovering state "+str(state))
        marking = state.marking
        for place in self.places:
            place.marking = marking[place.nid]

    def trace_status(self, step):
        print "########## "+ step +" ##############"
        print "base path: "+str(self.base_path)
        print "current path: "+str(self.current_path)
        print "path base: " + ', '.join(map(str, self.path_base))
        print "------------------------------------"
        print "base state: "+str(self.base_state)
        print "current state: "+str(self.current_state)
        print "state base: " + ', '.join(map(str, self.state_base))
        print "------------------------------------"
        print "restarted: " + str(self.restarted)
        print "####################################"

    def run_analysis_step(self):

        self.markings = []

        # self.trace_status("1. before solving place bindings...")

        # logging.info("resolution bindings on places")
        # logging.info("assign current marking")
        ## assign current marking
        for place in self.places:
            # logging.info("assigning " + place.nid + " to "+str(place.marking))
            self.p_prog.assign_external(Function(place.nid), place.marking)
        # logging.info("solving bindings on places...")
        self.p_prog.solve(on_model=self.update_pid)
        # logging.info("completed solving.")

        # self.trace_status("3. after solving place bindings...")

        next_events = None

        if self.bug is False:
            if self.restarted is False:
                self.path_base.remove(self.base_path)

        # the execution is complete if in the execution path we find the same state before the last one
        # if it is not complete, check for new events to fire
        if not (self.current_path.steps.index(self.current_state) + 1 < len(self.current_path.steps)):
            self.restarted = False

            ## consolidate the last computed state/path amongst all answer sets
            self.base_state = self.current_state
            self.base_path = self.current_path
            # self.trace_status("4. after settled bases...")

            next_events = self.current_state.find_next_events()
        # else:
            # logging.info("execution completed: found two times the same state in the same path.")

        # if it is complete, backtrack to uncovered events [depth-first search]
        if next_events is None:
            # logging.info("backtracking...")
            self.restarted = False

            # record this completed path
            # # logging.info("record the completed path...")
            # self.path_base.append(self.current_path)
            # print "completed path: "+', '.join(map(str, self.path_base))

            # go backwards until you don't find some next event to be covered
            for i in range(len(self.current_path.steps) - 2, -1, -1):
                # logging.info("checking at step "+str(i)+"...")

                step = self.current_path.steps[i]
                next_events = step.find_next_events()

                if next_events is not None:
                    # logging.info("found path still to be covered.")
                    self.restarted = True
                    self.current_state = step
                    self.current_path = self.current_path.clone(i)
                    self.load_state(step)
                    self.path_base.remove(self.base_path)
                    self.base_path = self.current_path
                    self.base_state = self.current_state
                    # self.trace_status("5. after succesful backtracking...")
                    break

        if next_events is None:

            if self.restarted is True:
                self.path_base.remove(self.base_path)

            # self.trace_status("6. after unsuccesful backtracking...")

            # logging.info("no new path to be covered.")
            return False
        else:
            # self.trace_status("7. before firing...")
            self.fire(next_events)
            self.last_events = next_events
            return True


class Path:

    def __init__(self):
        self.steps = []
        self.events_per_steps = []

    def __str__(self):
        output = ""
        for i in range(0, len(self.steps)):
            output += "(" + self.steps[i].sid + ")"
            if (i < len(self.steps) - 1):
               output += " -- " + str(self.events_per_steps[i]) + " -- "
        return output

    # shallow copy up to step n
    def clone(self, n=None):
        new_path = Path()
        assert (len(self.steps) == len(self.events_per_steps) + 1) or (len(self.steps) == 0 and len(self.events_per_steps) == 0)
        if n is None: n = len(self.steps)
        for i, step in enumerate(self.steps):
            if i <= n: new_path.steps.append(step)
        for i, events_per_step in enumerate(self.events_per_steps):
            if i <= n-1: new_path.events_per_steps.append(events_per_step)
        return new_path


class Group:

    def __init__(self, set=None):
        if set is None:
            self.set = []
        else:
            self.set = set

    def __len__(self):
        return len(self.set)

    def __hash__(self):
        key = ""
        for elem in sorted(self.set):
            key += str(elem)
        return hash(key)

    def __str__(self):
        output = ""
        for elem in self.set:
            output += str(elem) + ", "
        return output[:-2]

    def add(self, elem):
        if elem not in self.set:
            self.set.append(elem)



class State:

    def __init__(self, marking=None, sid=None):
        self.marking = marking
        self.sid = sid
        self.events_to_state = None

    def __str__(self):
        output = self.sid + " # "
        for nid in self.marking:
            output += nid + ": " + str(self.marking[nid]) + ", "
        output = output[:-2] + "; "
        if self.events_to_state is not None:
            for group in self.events_to_state:
                output += str(group) + " -> " + (self.events_to_state[group].sid if self.events_to_state[group] is not None else "None") + ", "
        return output[:-2]

    def find_next_events(self):
        next_events = None
        for key in self.events_to_state:
            if self.events_to_state[key] is None:
                next_events = key
                break
        return next_events
