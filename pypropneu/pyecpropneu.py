import logging
from pypropneu import PetriNetStructure, Place, Transition, ArcType, BindingOperator
from clingo import Control, parse_program
from timeit import default_timer as timer

class PetriNetEventCalculus(PetriNetStructure):

    def __init__(self, places=(), transitions=(), arcs=(), p_bindings=(), t_bindings=()):
        PetriNetStructure.__init__(self, places, transitions, arcs, p_bindings, t_bindings)

    @staticmethod
    def build_event_calculus_axioms():
        return """holdsAt(F, P, N) :-
  initially(F, P),
  not clipped(0, F, P, N),
  fluent(F), place(P), time(N).

holdsAt(F, P, N2) :-
  firesAt(T, N1), N1 < N2,
  initiates(T, F, P, N1),
  not clipped(N1, F, P, N2),
  place(P), transition(T), fluent(F), time(N1), time(N2).

clipped(N1, F, P, N2) :-
  firesAt(T, N), N1 <= N, N < N2,
  terminates(T, F, P, N),
  place(P), transition(T), fluent(F), time(N1), time(N2), time(N).
"""

    @staticmethod
    def build_operational_axioms():
        return """{prefiresAt(T, N)} :-
  enabled(T, N), transition(T), time(N).

someTransitionPrefiresAt(N) :-
  prefiresAt(T, N), transition(T), time(N).

:- not someTransitionPrefiresAt(0).
:- N > 0, not someTransitionPrefiresAt(N - 1), time(N).
:- prefiresAt(T1, N), prefiresAt(T2, N), T1 != T2, transition(T1), transition(T2), time(N).
"""
    @staticmethod
    def build_timerange(maxtime):
        return "time(0.."+str(maxtime)+")."

    @staticmethod
    def build_place(place):
        code = "place("+place.nid+").\n"
        code += "fluent(filled).\n"
        if place.marking is True:
            code += "initially(filled, "+place.nid+").\n"
        if len(place.outputs) > 1:
            transitions = []
            for output in place.outputs:
                if output.type == ArcType.NORMAL:
                    if output.target.__class__ is Transition:
                        transitions.append(output.target)
                else:
                    raise ValueError("Not yet implemented.")
            code += ":- 2{"
            for t in transitions:
                code += "terminates("+t.nid+", filled, "+place.nid+", N); "
            code = code[:-2]+"}.\n"
        return code

    def build_places(self):
        code = ""
        for place in self.places:
            code += self.build_place(place)
        return code

    @staticmethod
    def build_transition(transition):
        code = "transition("+transition.nid+").\n"

        normal_places = []
        inhibiting_places = []
        if len(transition.inputs) > 0:
            for input in transition.inputs:
                if input.type == ArcType.NORMAL:
                    if input.source.__class__ is Place:
                        normal_places.append(input.source)
                elif input.type == ArcType.INHIBITOR:
                    if input.source.__class__ is Place:
                        inhibiting_places.append(input.source)
                else:
                    raise ValueError("Not yet implemented.")
        if len(normal_places) > 0:
            code += "enabled("+transition.nid+", N) :- "
            for place in normal_places:
                code += "holdsAt(filled, "+place.nid+", N), "
            for place in inhibiting_places:
                code += "not holdsAt(filled, "+place.nid+", N), "
        code = code[:-2]+".\n"

        code += "firesAt("+transition.nid+", N) :- prefiresAt("+transition.nid+", N).\n"

        if len(normal_places) > 0:
            for place in normal_places:
                code += "terminates("+transition.nid+", filled, "+place.nid+", N) :- firesAt("+transition.nid+", N).\n"

        normal_places = []
        if len(transition.outputs) > 0:
            for output in transition.outputs:
                if output.type == ArcType.NORMAL:
                    if output.target.__class__ is Place:
                        normal_places.append(output.target)
                else:
                    raise ValueError("Not yet implemented.")
        if len(normal_places) > 0:
            for place in normal_places:
                code += "initiates("+transition.nid+", filled, "+place.nid+", N) :- firesAt("+transition.nid+", N).\n"

        return code

    @staticmethod
    def build_place_binding(binding):
        code = ""
        if binding.operator is BindingOperator.AND:
            if len(binding.outputs) != 1:
                raise ValueError("Wrong binding constraint")

            code += "holdsAt(filled, " + binding.outputs[0].target.nid + ", N) :- "
            for input in binding.inputs:
                code += "holdsAt(filled, " + input.source.nid + ", N), "
            code = code[:-2] + ".\n"
        elif binding.operator is BindingOperator.OR:
            if len(binding.outputs) != 1:
                raise ValueError("Wrong binding constraint")

            code += "holdsAt(filled, " + binding.outputs[0].target.nid + ", N) :- 1{"
            for input in binding.inputs:
                code += "holdsAt(filled, " + input.source.nid + ", N); "
            code = code[:-2] + "}.\n"
        elif binding.operator is BindingOperator.XOR:
            raise ValueError("Not yet implemented")
        elif binding.operator is BindingOperator.IMPLIES:
            if len(binding.outputs) != 1:
                raise ValueError("Wrong binding constraint")
            code += "holdsAt(filled, " + binding.outputs[0].target.nid + ", N) :- "
            for input in binding.inputs:
                code += "holdsAt(filled, " + input.source.nid + ", N), "
            code = code[:-2] + ".\n"
        elif binding.operator is BindingOperator.EQUIV:
            raise ValueError("Not yet implemented")
        return code

    @staticmethod
    def build_transition_binding(binding):
        code = ""
        if binding.operator is BindingOperator.IMPLIES:
            if len(binding.outputs) != 1:
                raise ValueError("Wrong binding constraint")
            elif binding.outputs[0].target.__class__ is not Transition:
                raise ValueError("Wrong binding constraint")

            transition = None
            for input in binding.inputs:
                if input.type == ArcType.NORMAL:
                    if input.source.__class__ is Transition:
                        if transition is None:
                            transition = input.source
                        else:
                            raise ValueError("Wrong binding constraint")
            if transition is None:
                raise ValueError("Wrong binding constraint")

            code += "firesAt(" + binding.outputs[0].target.nid + ", N) :- "

            normal_places = []
            inhibiting_places = []
            for input in binding.inputs:
                if input.type == ArcType.NORMAL:
                    if input.source.__class__ is Place:
                        normal_places.append(input.source)
                elif input.type == ArcType.INHIBITOR:
                    if input.source.__class__ is Place:
                        inhibiting_places.append(input.source)
                else:
                    raise ValueError("Not yet implemented.")

            for place in normal_places:
                code += "holdsAt(filled, "+place.nid+", N), "
            for place in inhibiting_places:
                code += "not holdsAt(filled, "+place.nid+", N), "

            code += "firesAt(" + transition.nid + ", N).\n"

        elif binding.operator is BindingOperator.EQUIV:
            raise ValueError("Not yet implemented")
        return code

    def build_transitions(self):
        code = ""
        for transition in self.transitions:
            code += self.build_transition(transition)
        return code

    def build_place_bindings(self):
        code = ""
        for binding in self.p_bindings:
            code += self.build_place_binding(binding)
        return code

    def build_transition_bindings(self):
        code = ""
        for binding in self.t_bindings:
            code += self.build_transition_binding(binding)
        return code

    def build_event_calculus_program(self, maxtime):
        code = ""
        code += "% Event Calculus axioms \n" + self.build_event_calculus_axioms() + "\n"
        code += "% Operational axioms \n" + self.build_operational_axioms() + "\n"
        code += "% Places \n" + self.build_places() + "\n"
        code += "% Transitions \n" + self.build_transitions() + "\n"
        code += "% Bindings on places \n" + self.build_place_bindings() + "\n"
        code += "% Bindings on transitions \n" + self.build_transition_bindings() + "\n"
        code += "% Time range \n" + self.build_timerange(maxtime)
        return code

    def update_n_models(self, model):
        self.n_models += 1

    def solve(self, maxtime):
        self.n_models = 0

        code = self.build_event_calculus_program(maxtime)

        out_file = open("../tmp/ec.lp", "w")
        out_file.write(code)
        out_file.close()

        ## create the ASP solver control for
        prg = Control()
        prg.configuration.solve.models = 0  # to obtain all answer sets

        with prg.builder() as builder:
            parse_program(code, lambda statement: builder.add(statement))
        prg.ground([("base", [])])

        start = timer()
        prg.solve(on_model=self.update_n_models, assumptions=())
        end = timer()

        timing = end - start
        print str(self.n_models) + " answer sets found in " + str(timing) + " ms."

        return (self.n_models, timing)
