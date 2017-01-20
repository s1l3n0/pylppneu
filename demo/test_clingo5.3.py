from clingo import Control, Function, parse_program

def on_model(model):
    output = ""
    for atom in model.symbols(shown=True):
        output += str(atom) + ", "
    if output != "":
        print output[:-2]

ctl = Control()
ctl.configuration.solve.models = 0              # for all answer sets
with ctl.builder() as builder:
    parse_program("""#external p1.
#external p2.
#external p3.
#external p4.
#external p5.
p4 :- p1, p2.""", lambda statement: builder.add(statement))
ctl.ground([("base", [])])

ctl.assign_external(Function("p1"), True)
ctl.assign_external(Function("p2"), False)
ctl.assign_external(Function("p3"), False)
ctl.assign_external(Function("p4"), False)
ctl.assign_external(Function("p5"), False)

ctl.solve(on_model=on_model)
